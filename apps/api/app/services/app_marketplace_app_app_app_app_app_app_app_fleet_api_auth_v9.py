"""Fleet API Auth v9 — track API authentication method distribution."""
from __future__ import annotations
def fleet_api_auth_v9(endpoints: list[dict]) -> dict:
    jwt = [e for e in endpoints if e.get("auth") == "jwt"]
    api_key = [e for e in endpoints if e.get("auth") == "api_key"]
    oauth = [e for e in endpoints if e.get("auth") == "oauth2"]
    public = [e for e in endpoints if e.get("auth") == "none"]
    return {"endpoints": len(endpoints), "jwt": len(jwt), "api_key": len(api_key),
            "oauth2": len(oauth), "public": len(public), "healthy": len(public) < len(endpoints) * 0.1}
