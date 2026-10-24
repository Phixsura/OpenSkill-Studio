"""Resource lifecycle manager — track resources from creation to deletion."""
from __future__ import annotations
import time


def create_resource(name: str, resource_type: str, owner: str, ttl_days: int = 0) -> dict:
    return {"name": name, "type": resource_type, "owner": owner,
            "status": "active", "created_at": time.time(),
            "expires_at": time.time() + ttl_days * 86400 if ttl_days > 0 else 0,
            "has_ttl": ttl_days > 0}


def audit_resources(resources: list[dict], now: float | None = None) -> dict:
    now = now or time.time()
    expired = [r for r in resources if r["has_ttl"] and now > r["expires_at"]]
    orphaned = [r for r in resources if not r.get("owner")]
    by_type: dict[str, int] = {}
    for r in resources:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    return {"total": len(resources), "active": len(resources) - len(expired),
            "expired": len(expired), "orphaned": len(orphaned),
            "by_type": by_type, "needs_cleanup": len(expired) + len(orphaned)}
