from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_signer import sign_payload, verify_signature, _DEFAULT_KEY

def test_sign_verify():
    payload = {"event": "app.installed", "app_id": "myapp"}
    signed = sign_payload(payload, timestamp=1000000)
    assert signed["signature"].startswith("v1=")
    v = verify_signature(payload, header=signed["header"], now=1000000)
    assert v["valid"]

def test_expired():
    payload = {"event": "test"}
    signed = sign_payload(payload, timestamp=1000)
    v = verify_signature(payload, header=signed["header"], now=2000)
    assert not v["valid"]
    assert v["reason"] == "timestamp_expired"

def test_tampered():
    payload = {"event": "test"}
    signed = sign_payload(payload, timestamp=1000)
    v = verify_signature({"event": "hacked"}, header=signed["header"], now=1000)
    assert not v["valid"]
    assert v["reason"] == "signature_mismatch"
