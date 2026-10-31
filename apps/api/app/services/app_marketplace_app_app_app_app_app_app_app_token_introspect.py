"""Token introspection — inspect and validate access tokens."""
from __future__ import annotations
import time


def introspect_token(token_data: dict) -> dict:
    active = token_data.get("active", True)
    exp = token_data.get("exp", 0)
    expired = exp > 0 and exp < time.time()
    scopes = token_data.get("scopes", [])
    return {"active": active and not expired, "expired": expired,
            "subject": token_data.get("sub", ""),
            "issuer": token_data.get("iss", ""),
            "scopes": scopes, "scope_count": len(scopes),
            "token_type": token_data.get("token_type", "bearer"),
            "client_id": token_data.get("client_id", "")}


def check_token_permissions(token: dict, required_scopes: list[str]) -> dict:
    granted = set(token.get("scopes", []))
    missing = [s for s in required_scopes if s not in granted]
    return {"authorized": len(missing) == 0, "granted": sorted(granted),
            "required": required_scopes, "missing": missing}
