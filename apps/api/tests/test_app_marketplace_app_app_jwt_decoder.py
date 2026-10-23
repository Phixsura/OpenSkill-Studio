import base64, json
from app.services.app_marketplace_app_app_jwt_decoder import decode_jwt

def _make_jwt(header, payload):
    h = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    return f"{h}.{p}.fakesig"

def test_decode():
    token = _make_jwt({"alg": "HS256", "typ": "JWT"}, {"sub": "user_1", "iss": "openskill"})
    r = decode_jwt(token=token)
    assert r["valid"]
    assert r["algorithm"] == "HS256"
    assert r["subject"] == "user_1"
    assert r["issuer"] == "openskill"

def test_expired():
    token = _make_jwt({"alg": "RS256"}, {"sub": "u1", "exp": 1000000})
    r = decode_jwt(token=token)
    assert r["expired"]

def test_invalid():
    r = decode_jwt(token="not.valid")
    assert not r["valid"]
