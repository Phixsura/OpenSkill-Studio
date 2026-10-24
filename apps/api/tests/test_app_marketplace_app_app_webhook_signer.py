from app.services.app_marketplace_app_app_webhook_signer import sign_webhook, verify_webhook, generate_webhook_secret
import json

def test_sign():
    r = sign_webhook(payload={"event": "test"}, secret="mysecret")
    assert r["signature"].startswith("v1=")
    assert "X-Webhook-Signature" in r["headers"]

def test_verify():
    secret = "test_secret"
    payload = {"event": "installed"}
    signed = sign_webhook(payload=payload, secret=secret)
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    r = verify_webhook(payload=body, signature=signed["signature"],
                       timestamp=signed["timestamp"], secret=secret, max_age_s=60)
    assert r["valid"]
    assert r["signature_match"]

def test_bad_secret():
    signed = sign_webhook(payload={"x": 1}, secret="correct")
    body = json.dumps({"x": 1}, sort_keys=True, separators=(",", ":"))
    r = verify_webhook(payload=body, signature=signed["signature"],
                       timestamp=signed["timestamp"], secret="wrong", max_age_s=60)
    assert not r["signature_match"]

def test_generate_secret():
    r = generate_webhook_secret()
    assert r["secret"].startswith("whsec_")
    assert r["length"] > 30
