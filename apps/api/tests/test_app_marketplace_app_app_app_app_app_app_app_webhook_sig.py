from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_sig import sign_payload, verify_signature
import time

def test_sign_and_verify():
    ts = int(time.time())
    r = sign_payload('{"event":"test"}', "secret123", timestamp=ts)
    assert r["signature"].startswith("v1=")
    v = verify_signature('{"event":"test"}', r["header"], "secret123")
    assert v["valid"]

def test_bad_sig():
    ts = int(time.time())
    v = verify_signature("payload", f"t={ts},v1=badsig", "secret123")
    assert not v["valid"]
    assert v["error"] == "signature_mismatch"

def test_expired():
    old_ts = int(time.time()) - 600
    r = sign_payload("data", "s", timestamp=old_ts)
    v = verify_signature("data", r["header"], "s", tolerance_sec=300)
    assert not v["valid"]
    assert v["error"] == "timestamp_expired"
