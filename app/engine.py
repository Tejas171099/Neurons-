"""Orchestrates analysis with the 2-second fail-safe."""
import asyncio
import time

from .auth_checks import run_all
from .parser import parse_email
from .spoof import detect_spoof

HARD_TIMEOUT_S = 2.0


def _risk(spoofed: bool, spf: str, dkim: str, dmarc: str) -> str:
    bad_auth = sum(x in ("fail", "softfail", "permerror") for x in (spf, dkim, dmarc))
    if spoofed and bad_auth >= 1:
        return "CRITICAL"
    if spoofed or dmarc == "fail":
        return "HIGH"
    if bad_auth:
        return "MEDIUM"
    return "LOW"


def _under_review(reason: str, started: float, parsed=None) -> dict:
    return {
        "status": "under_review", "risk_level": "UNDER_REVIEW", "is_spoofed": None,
        "display_name": getattr(parsed, "display_name", None),
        "actual_sender": getattr(parsed, "sender_email", None),
        "spf_valid": None, "dkim_valid": None, "dmarc_valid": None,
        "reasons": [reason], "scan_ms": round((time.perf_counter() - started) * 1000),
    }


async def analyze(raw: bytes) -> dict:
    """Never raises, never blocks longer than HARD_TIMEOUT_S. The email body is never stored or logged."""
    t0 = time.perf_counter()
    try:
        parsed = parse_email(raw)  # cheap, local - safe to do before the timeout
    except Exception:
        return _under_review("Could not parse message", t0)

    spoof = detect_spoof(parsed.display_name, parsed.sender_domain)  # local, instant

    try:
        auth = await asyncio.wait_for(asyncio.to_thread(run_all, parsed), timeout=HARD_TIMEOUT_S)
    except asyncio.TimeoutError:
        return _under_review(f"Validation exceeded {HARD_TIMEOUT_S}s - fail-safe triggered", t0, parsed)
    except Exception:
        return _under_review("Validation error - fail-safe triggered", t0, parsed)

    spf_ok, dkim_ok, dmarc_ok = (auth["spf"] == "pass", auth["dkim"] == "pass", auth["dmarc"] == "pass")
    reasons = [spoof.reason] if spoof.is_spoofed else []
    if not spf_ok:
        reasons.append(f"SPF {auth['spf']}")
    if not dkim_ok:
        reasons.append(f"DKIM {auth['dkim']}")
    if not dmarc_ok:
        reasons.append(f"DMARC {auth['dmarc']}")

    return {
        "status": "success",
        "is_spoofed": spoof.is_spoofed,
        "display_name": parsed.display_name,
        "actual_sender": parsed.sender_email,
        "spf_valid": spf_ok,
        "dkim_valid": dkim_ok,
        "dmarc_valid": dmarc_ok,
        "risk_level": _risk(spoof.is_spoofed, auth["spf"], auth["dkim"], auth["dmarc"]),
        "reasons": reasons,
        "auth_source": auth["source"],
        "scan_ms": round((time.perf_counter() - t0) * 1000),
    }
