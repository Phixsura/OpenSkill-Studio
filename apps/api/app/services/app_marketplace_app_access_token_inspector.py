"""Access token inspector — decode and display JWT token claims."""

import base64
import json
from datetime import datetime


def decode_jwt_claims(*, token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {"error": "Invalid JWT format (expected 3 parts)"}
    try:
        payload = parts[1]
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        decoded = base64.urlsafe_b64decode(payload)
        claims = json.loads(decoded)
    except Exception:
        return {"error": "Failed to decode token payload"}
    exp = claims.get("exp")
    expired = False
    if exp:
        expired = datetime.utcnow().timestamp() > exp
    return {
        "claims": claims,
        "subject": claims.get("sub"),
        "issuer": claims.get("iss"),
        "audience": claims.get("aud"),
        "expires_at": datetime.fromtimestamp(exp).isoformat() if exp else None,
        "expired": expired,
        "scopes": claims.get("scope", "").split() if claims.get("scope") else [],
    }
