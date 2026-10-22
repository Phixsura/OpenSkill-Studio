from app.services.app_marketplace_app_webhook_signature import sign_payload, verify_signature

def test_sign_and_verify():
    result = sign_payload(payload='{"event":"test"}', secret="mysecret", timestamp=1000000)
    v = verify_signature(payload='{"event":"test"}', secret="mysecret", header=result["header"], tolerance_seconds=999999999)
    assert v["valid"]

def test_wrong_secret():
    result = sign_payload(payload='{"event":"test"}', secret="mysecret", timestamp=1000000)
    v = verify_signature(payload='{"event":"test"}', secret="wrong", header=result["header"], tolerance_seconds=999999999)
    assert not v["valid"]

def test_tampered_payload():
    result = sign_payload(payload='{"event":"test"}', secret="mysecret", timestamp=1000000)
    v = verify_signature(payload='{"event":"hacked"}', secret="mysecret", header=result["header"], tolerance_seconds=999999999)
    assert not v["valid"]
