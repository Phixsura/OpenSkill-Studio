"""JWT token inspector — decode and validate JWT structure."""
from __future__ import annotations
import base64
import json
import time


def decode_jwt(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {"valid": False, "error": "invalid_format"}
    try:
        header_b64 = parts[0] + "=" * (-len(parts[0]) % 4)
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64))
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception:
        return {"valid": False, "error": "decode_failed"}
    exp = payload.get("exp")
    expired = exp is not None and exp < time.time()
    return {"valid": True, "header": header, "payload": payload,
            "algorithm": header.get("alg", "unknown"),
            "expired": expired, "claims": list(payload.keys())}


def analyze_claims(payload: dict) -> dict:
    standard = {"iss", "sub", "aud", "exp", "nbf", "iat", "jti"}
    found_standard = sorted(set(payload.keys()) & standard)
    custom = sorted(set(payload.keys()) - standard)
    has_expiry = "exp" in payload
    return {"standard_claims": found_standard, "custom_claims": custom,
            "has_expiry": has_expiry, "total_claims": len(payload)}
