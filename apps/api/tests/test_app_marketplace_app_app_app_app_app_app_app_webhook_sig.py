from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_sig import sign_payload, verify_signature

def test_sign_verify():
    payload = '{"event":"order.created"}'
    secret = "whsec_test123"
    signed = sign_payload(payload, secret)
    assert signed["algorithm"] == "sha256"
    r = verify_signature(payload, secret, signed["signature"])
    assert r["valid"]

def test_invalid():
    r = verify_signature("payload", "secret", "wrong_sig")
    assert not r["valid"]
