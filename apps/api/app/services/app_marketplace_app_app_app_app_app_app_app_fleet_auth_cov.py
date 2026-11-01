"""Fleet API auth coverage — track authentication adoption."""
from __future__ import annotations
def fleet_auth_coverage(endpoints: list[dict]) -> dict:
    authenticated = [e for e in endpoints if e.get("requires_auth", False)]
    public = len(endpoints) - len(authenticated)
    return {"total": len(endpoints), "authenticated": len(authenticated),
            "public": public, "fully_protected": public == 0}
