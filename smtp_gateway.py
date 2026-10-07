"""Optional: real SMTP listener for scan@yourguard.ai (needs MX record + port 25 + TLS in production).
Run: python smtp_gateway.py   -> forwards each message to the scan engine in memory only."""
import asyncio

from aiosmtpd.controller import Controller

from app.engine import analyze


class Handler:
    async def handle_DATA(self, server, session, envelope):
        result = await analyze(envelope.content)  # ephemeral: not persisted
        # TODO: push `result` to the UI (webhook / websocket / reply email to envelope.mail_from)
        print({k: result[k] for k in ("actual_sender", "risk_level", "scan_ms")})
        return "250 Message accepted for analysis"


if __name__ == "__main__":
    Controller(Handler(), hostname="0.0.0.0", port=8025).start()
    asyncio.get_event_loop().run_forever()
