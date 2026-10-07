# YourGuard – Email Gateway & Header Authentication Engine

    pip install -r requirements.txt
    uvicorn app.main:app --reload
    pytest

Try it:

    curl -X POST localhost:8000/v1/scan/raw --data-binary @sample.eml

| Endpoint | Purpose |
|---|---|
| POST /v1/scan/raw | Mode B – raw RFC-822 body |
| POST /v1/scan/upload | Mode B – upload .eml |
| POST /v1/inbound | Mode B – SendGrid/Mailgun inbound webhook for scan@yourguard.ai |
| POST /v1/oauth/gmail/scan | Mode A – Gmail (Bearer token, gmail.readonly) |
| POST /v1/oauth/graph/scan | Mode A – Microsoft Graph (Bearer token, Mail.Read) |

Privacy: bodies live only in request memory; nothing is written to a DB, disk or logs.
2s fail-safe: `engine.HARD_TIMEOUT_S` -> returns `risk_level: UNDER_REVIEW`.
