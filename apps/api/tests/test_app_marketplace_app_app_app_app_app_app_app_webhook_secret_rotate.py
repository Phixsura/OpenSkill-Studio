import hmac, hashlib
from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_secret_rotate import WebhookSecretRotator

def test_rotate():
    r = WebhookSecretRotator()
    reg = r.register("wh1")
    old_secret = reg["secret"]
    payload = "test_payload"
    old_sig = hmac.new(old_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    # Verify with current secret
    v = r.verify("wh1", payload=payload, signature=old_sig)
    assert v["valid"]
    assert v["matched"] == "current"
    # Rotate
    rot = r.rotate("wh1")
    new_sig = hmac.new(rot["new_secret"].encode(), payload.encode(), hashlib.sha256).hexdigest()
    # New secret works
    v2 = r.verify("wh1", payload=payload, signature=new_sig)
    assert v2["valid"]
    # Old secret works during grace period
    v3 = r.verify("wh1", payload=payload, signature=old_sig)
    assert v3["valid"]
    assert v3["matched"] == "previous"
