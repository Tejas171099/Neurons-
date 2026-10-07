import asyncio
from unittest.mock import patch

from app import engine
from app.spoof import detect_spoof

SPOOF = (b"From: \"Amazon Support\" <service@amzn-billing-alert.xyz>\r\n"
         b"Return-Path: <service@amzn-billing-alert.xyz>\r\n"
         b"Subject: Amazon Order Confirmation\r\n"
         b"Authentication-Results: mx.google.com; spf=fail; dkim=none; dmarc=fail\r\n\r\nhi")


def test_sbi_spoof():
    assert detect_spoof("State Bank of India", "sbi-online-fix.top").is_spoofed
    assert not detect_spoof("Netflix", "netflix.com").is_spoofed
    assert not detect_spoof("Netflix", "mailer.netflix.com").is_spoofed


def test_amazon_example():
    r = asyncio.run(engine.analyze(SPOOF))
    assert r["is_spoofed"] and not r["spf_valid"] and not r["dmarc_valid"]
    assert r["risk_level"] == "CRITICAL"


def test_timeout_failsafe():
    import time
    with patch.object(engine, "HARD_TIMEOUT_S", 0.2), patch.object(engine, "run_all", lambda e: time.sleep(1)):
        r = asyncio.run(engine.analyze(SPOOF))
    assert r["status"] == "under_review"
