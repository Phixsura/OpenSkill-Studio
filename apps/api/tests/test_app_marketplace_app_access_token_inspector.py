import base64, json, time
from app.services.app_marketplace_app_access_token_inspector import decode_jwt_claims

def _make_jwt(claims):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
    return f"{header}.{payload}.fakesig"

def test_decode():
    token = _make_jwt({"sub": "user_1", "iss": "openskill", "exp": int(time.time()) + 3600, "scope": "read write"})
    r = decode_jwt_claims(token=token)
    assert r["subject"] == "user_1"
    assert r["issuer"] == "openskill"
    assert not r["expired"]
    assert "read" in r["scopes"]

def test_expired():
    token = _make_jwt({"sub": "u1", "exp": 1000000000})
    r = decode_jwt_claims(token=token)
    assert r["expired"]

def test_invalid():
    r = decode_jwt_claims(token="not.a.valid.jwt.token")
    assert "error" in r
