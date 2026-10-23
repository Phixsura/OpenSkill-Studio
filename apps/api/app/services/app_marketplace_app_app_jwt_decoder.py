"""JWT decoder — decode and inspect JWT tokens (no verification)."""

import base64
import json
import html
from datetime import datetime, timezone


def decode_jwt(*, token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {"valid": False, "error": "JWT must have 3 parts (header.payload.signature)"}
    try:
        header_b64 = parts[0] + "=" * (4 - len(parts[0]) % 4)
        payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64))
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception as e:
        return {"valid": False, "error": f"Decode error: {str(e)}"}

    exp = payload.get("exp")
    iat = payload.get("iat")
    expired = False
    if exp:
        expired = datetime.now(timezone.utc).timestamp() > exp

    return {"valid": True, "header": header, "payload": payload,
            "algorithm": header.get("alg", "unknown"),
            "subject": payload.get("sub"),
            "issuer": payload.get("iss"),
            "expired": expired,
            "claims": list(payload.keys())}
