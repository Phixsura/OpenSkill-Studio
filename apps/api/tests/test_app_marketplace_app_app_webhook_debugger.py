import hmac, hashlib
from app.services.app_marketplace_app_app_webhook_debugger import create_debug_endpoint, inspect_delivery, get_debug_stats

def test_create():
    r = create_debug_endpoint(app_id="a1")
    assert "debug.openskill.dev" in r["url"]
    assert r["expires_in_hours"] == 24

def test_inspect_valid_sig():
    secret = "my_secret"
    payload = '{"event":"test"}'
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    r = inspect_delivery(payload=payload, headers={"Content-Type": "application/json", "X-Signature": sig}, secret=secret)
    assert r["signature_valid"] is True
    assert r["has_signature"]

def test_inspect_invalid_sig():
    r = inspect_delivery(payload="data", headers={"X-Signature": "wrong"}, secret="secret")
    assert r["signature_valid"] is False

def test_stats():
    deliveries = [{"payload_size": 100, "signature_valid": True},
                  {"payload_size": 200, "signature_valid": False}]
    r = get_debug_stats(deliveries=deliveries)
    assert r["total_deliveries"] == 2
    assert r["valid_signatures"] == 1
    assert r["avg_payload_size"] == 150
