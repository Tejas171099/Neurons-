"""Mode A: OAuth2 read-only fetchers. The OAuth *flow* (consent screen, token exchange) lives in your
frontend/auth service; this module just uses the resulting short-lived access token. Tokens are never stored."""
import base64

import httpx

GMAIL = "https://gmail.googleapis.com/gmail/v1/users/me"
GRAPH = "https://graph.microsoft.com/v1.0/me"
# Scopes needed: https://www.googleapis.com/auth/gmail.readonly  |  Mail.Read (Graph)


async def fetch_gmail_unread(token: str, limit: int = 10) -> list[bytes]:
    h = {"Authorization": f"Bearer {token}"}
    q = {"q": "is:unread (invoice OR receipt OR order OR billing OR payment)", "maxResults": limit}
    async with httpx.AsyncClient(timeout=10, headers=h) as c:
        r = await c.get(f"{GMAIL}/messages", params=q)
        r.raise_for_status()
        out = []
        for m in r.json().get("messages", []):
            raw = await c.get(f"{GMAIL}/messages/{m['id']}", params={"format": "raw"})
            raw.raise_for_status()
            out.append(base64.urlsafe_b64decode(raw.json()["raw"] + "=="))
        return out


async def fetch_graph_unread(token: str, limit: int = 10) -> list[bytes]:
    h = {"Authorization": f"Bearer {token}"}
    p = {"$filter": "isRead eq false", "$top": limit, "$select": "id"}
    async with httpx.AsyncClient(timeout=10, headers=h) as c:
        r = await c.get(f"{GRAPH}/messages", params=p)
        r.raise_for_status()
        out = []
        for m in r.json().get("value", []):
            mime = await c.get(f"{GRAPH}/messages/{m['id']}/$value")  # full MIME incl. headers
            mime.raise_for_status()
            out.append(mime.content)
        return out
