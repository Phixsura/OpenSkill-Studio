"""Fleet access review — track periodic access review completion."""
from __future__ import annotations
def fleet_access_review(users: list[dict]) -> dict:
    reviewed = [u for u in users if u.get("reviewed", False)]
    excess = [u for u in users if u.get("excess_permissions", False)]
    return {"total": len(users), "reviewed": len(reviewed),
            "pending_review": len(users) - len(reviewed),
            "excess_permissions": len(excess), "clean": len(excess) == 0}
