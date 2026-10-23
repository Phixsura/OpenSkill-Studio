from app.services.app_marketplace_app_webhook_signature import sign_payload, verify_signature, generate_webhook_secret
import time

def test_sign_verify():
    secret = "test_secret_key"
    payload = '{"event": "app.installed"}'
    ts = int(time.time())
    signed = sign_payload(payload=payload, secret=secret, timestamp=ts)
    result = verify_signature(payload=payload, header=signed["header"], secret=secret)
    assert result["valid"]

def test_wrong_secret():
    payload = "data"
    ts = int(time.time())
    signed = sign_payload(payload=payload, secret="correct", timestamp=ts)
    result = verify_signature(payload=payload, header=signed["header"], secret="wrong")
    assert not result["valid"]
    assert "mismatch" in result["error"]

def test_malformed():
    result = verify_signature(payload="x", header="garbage", secret="s")
    assert not result["valid"]

def test_generate():
    r = generate_webhook_secret()
    assert r["secret"].startswith("whsec_")
    assert len(r["secret"]) > 20
