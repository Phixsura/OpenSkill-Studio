import hmac, hashlib
from app.services.app_marketplace_app_app_app_app_app_app_app_payment_webhook import verify_webhook, process_event

def test_verify():
    payload = '{"event":"payment.completed"}'
    secret = "whsec_test123"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    r = verify_webhook(payload, sig, secret)
    assert r["valid"]
    r2 = verify_webhook(payload, "badsig", secret)
    assert not r2["valid"]

def test_process():
    r = process_event("payment.completed", {"amount": 9900, "currency": "USD", "customer": "cus_123"})
    assert r["processed"]
    assert r["action"] == "activate_subscription"
    r2 = process_event("unknown.event", {})
    assert not r2["processed"]
