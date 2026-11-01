import base64, json
from app.services.app_marketplace_app_app_app_app_app_app_app_jwt_inspector import decode_jwt, analyze_claims

def _make_jwt(header, payload):
    h = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    p = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"{h}.{p}.fakesig"

def test_decode():
    token = _make_jwt({"alg": "HS256", "typ": "JWT"}, {"sub": "user1", "exp": 9999999999})
    r = decode_jwt(token)
    assert r["valid"]
    assert r["algorithm"] == "HS256"
    assert not r["expired"]
    assert "sub" in r["claims"]

def test_invalid():
    assert not decode_jwt("not.a.valid.token.here")["valid"]
    assert not decode_jwt("bad")["valid"]

def test_claims():
    r = analyze_claims({"sub": "u1", "exp": 123, "role": "admin", "org": "acme"})
    assert "sub" in r["standard_claims"]
    assert "role" in r["custom_claims"]
    assert r["has_expiry"]
