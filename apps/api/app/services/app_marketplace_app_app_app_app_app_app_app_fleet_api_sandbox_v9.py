"""Fleet API Sandbox v9 — track developer sandbox API environments."""
from __future__ import annotations
def fleet_api_sandbox_v9(sandboxes: list[dict]) -> dict:
    active = [s for s in sandboxes if s.get("active")]
    requests = sum(s.get("requests_today", 0) for s in sandboxes)
    users = len({s.get("user") for s in sandboxes if s.get("user")})
    return {"sandboxes": len(sandboxes), "active": len(active), "requests_today": requests,
            "unique_users": users, "healthy": True}
