from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_sig import sign_payload, verify_signature
import time

def test_sign_verify():
    payload = '{"event":"order.created"}'
    secret = "whsec_test123"
    ts = int(time.time())
    signed = sign_payload(payload, secret, timestamp=ts)
    assert signed["algorithm"] == "sha256"
    r = verify_signature(payload, secret, signed["signature"], timestamp=ts)
    assert r["valid"]

def test_invalid_sig():
    r = verify_signature("payload", "secret", "wrong_sig", timestamp=int(time.time()))
    assert not r["valid"]
    assert r["reason"] == "signature_mismatch"

def test_expired_timestamp():
    r = verify_signature("payload", "secret", "any", timestamp=1000, tolerance_seconds=300)
    assert not r["valid"]
    assert r["reason"] == "timestamp_expired"
