import time
from app.services.app_marketplace_app_webhook_signature import sign_payload, verify_signature

def test_sign_and_verify():
    ts = int(time.time())
    result = sign_payload(payload='{"event":"test"}', secret="mysecret", timestamp=ts)
    v = verify_signature(payload='{"event":"test"}', secret="mysecret", header=result["header"])
    assert v["valid"]

def test_wrong_secret():
    ts = int(time.time())
    result = sign_payload(payload='{"event":"test"}', secret="mysecret", timestamp=ts)
    v = verify_signature(payload='{"event":"test"}', secret="wrong", header=result["header"])
    assert not v["valid"]

def test_tampered_payload():
    ts = int(time.time())
    result = sign_payload(payload='{"event":"test"}', secret="mysecret", timestamp=ts)
    v = verify_signature(payload='{"event":"hacked"}', secret="mysecret", header=result["header"])
    assert not v["valid"]
