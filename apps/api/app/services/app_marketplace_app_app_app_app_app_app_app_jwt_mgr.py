"""JWT token manager — issue and validate JWT-like tokens."""
from __future__ import annotations
import hashlib, secrets, time, json, base64


def _b64encode(data: str) -> str:
    return base64.urlsafe_b64encode(data.encode()).rstrip(b"=").decode()


def create_token(subject: str, claims: dict, secret: str, ttl: int = 3600) -> dict:
    now = int(time.time())
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}))
    payload_data = {"sub": subject, "iat": now, "exp": now + ttl, **claims}
    payload = _b64encode(json.dumps(payload_data))
    sig_input = f"{header}.{payload}"
    signature = hashlib.sha256(f"{sig_input}.{secret}".encode()).hexdigest()[:32]
    token = f"{header}.{payload}.{signature}"
    return {"token": token, "expires_at": now + ttl}


def validate_token(token: str, secret: str, now: int | None = None) -> dict:
    now = now or int(time.time())
    parts = token.split(".")
    if len(parts) != 3:
        return {"valid": False, "reason": "malformed"}
    header, payload, sig = parts
    expected_sig = hashlib.sha256(f"{header}.{payload}.{secret}".encode()).hexdigest()[:32]
    if not secrets.compare_digest(sig, expected_sig):
        return {"valid": False, "reason": "invalid_signature"}
    try:
        payload_bytes = base64.urlsafe_b64decode(payload + "==")
        claims = json.loads(payload_bytes)
    except Exception:
        return {"valid": False, "reason": "decode_error"}
    if claims.get("exp", 0) < now:
        return {"valid": False, "reason": "expired"}
    return {"valid": True, "subject": claims.get("sub"), "claims": claims}
