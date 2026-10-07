"""YourGuard - Email Gateway & Header Authentication Engine.   Run: uvicorn app.main:app --reload"""
import asyncio

from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile
from pydantic import BaseModel

from . import ingest
from .engine import analyze

app = FastAPI(title="YourGuard Email Gateway", version="0.1.0")
MAX_BYTES = 10 * 1024 * 1024  # 10 MB cap


# ---------- Mode B: Virtual gateway / forwarding endpoint ----------
@app.post("/v1/scan/raw")
async def scan_raw(request: Request):
    """POST the raw RFC-822 message (Content-Type: message/rfc822 or text/plain)."""
    raw = await request.body()
    if not raw or len(raw) > MAX_BYTES:
        raise HTTPException(400, "Empty or oversized message")
    return await analyze(raw)


@app.post("/v1/scan/upload")
async def scan_upload(file: UploadFile = File(...)):
    """Upload a .eml file."""
    raw = await file.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise HTTPException(400, "Empty or oversized message")
    return await analyze(raw)


@app.post("/v1/inbound")
async def inbound_webhook(request: Request):
    """Inbound-parse webhook for scan@yourguard.ai (SendGrid / Mailgun / Postmark 'raw MIME' mode).
    Mailgun: field 'body-mime'; SendGrid: field 'email' (enable 'send raw')."""
    form = await request.form()
    raw = form.get("email") or form.get("body-mime")
    if raw is None:
        raise HTTPException(400, "No raw MIME field found")
    raw = (await raw.read()) if hasattr(raw, "read") else str(raw).encode()
    return await analyze(raw)


# ---------- Mode A: OAuth read-only ----------
class ScanRequest(BaseModel):
    limit: int = 10


@app.post("/v1/oauth/gmail/scan")
async def gmail_scan(body: ScanRequest, authorization: str = Header(...)):
    msgs = await ingest.fetch_gmail_unread(authorization.removeprefix("Bearer ").strip(), body.limit)
    return {"status": "success", "results": await asyncio.gather(*(analyze(m) for m in msgs))}


@app.post("/v1/oauth/graph/scan")
async def graph_scan(body: ScanRequest, authorization: str = Header(...)):
    msgs = await ingest.fetch_graph_unread(authorization.removeprefix("Bearer ").strip(), body.limit)
    return {"status": "success", "results": await asyncio.gather(*(analyze(m) for m in msgs))}


@app.get("/health")
async def health():
    return {"ok": True}
