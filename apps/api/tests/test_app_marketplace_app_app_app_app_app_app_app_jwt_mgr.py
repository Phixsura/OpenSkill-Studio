from app.services.app_marketplace_app_app_app_app_app_app_app_jwt_mgr import create_token, validate_token
import time

def test_create_validate():
    r = create_token("user-1", {"role": "admin"}, "my-secret", ttl=60)
    v = validate_token(r["token"], "my-secret")
    assert v["valid"]
    assert v["subject"] == "user-1"
    assert v["claims"]["role"] == "admin"

def test_invalid_sig():
    r = create_token("user-1", {}, "secret1")
    v = validate_token(r["token"], "wrong-secret")
    assert not v["valid"]
    assert v["reason"] == "invalid_signature"

def test_expired():
    r = create_token("user-1", {}, "secret", ttl=10)
    v = validate_token(r["token"], "secret", now=int(time.time()) + 20)
    assert not v["valid"]
    assert v["reason"] == "expired"
