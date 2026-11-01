from app.services.app_marketplace_app_app_webhook_secret import generate_secret, verify_payload
import hmac, hashlib, time

def test_generate():
    r = generate_secret()
    assert r["secret"].startswith("whsec_")
    assert "••••" in r["preview"]

def test_verify_valid():
    secret = "test_secret_key"
    payload = '{"event":"test"}'
    ts = int(time.time())
    sig = "v1=" + hmac.new(secret.encode(), f"{ts}.{payload}".encode(), hashlib.sha256).hexdigest()
    r = verify_payload(payload=payload, secret=secret, signature=sig, timestamp=ts)
    assert r["valid"]
    assert r["signature_valid"]

def test_verify_bad_sig():
    r = verify_payload(payload="x", secret="s", signature="v1=bad", timestamp=int(time.time()))
    assert not r["valid"]
