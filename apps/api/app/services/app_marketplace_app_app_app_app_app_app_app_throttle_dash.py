"""Request throttle dashboard — unified throttle view across all tenants."""
from __future__ import annotations
from collections import defaultdict


def throttle_dashboard(events: list[dict]) -> dict:
    by_tenant: dict[str, dict] = defaultdict(lambda: {"allowed": 0, "throttled": 0})
    for e in events:
        tid = e.get("tenant_id", "unknown")
        if e.get("throttled"):
            by_tenant[tid]["throttled"] += 1
        else:
            by_tenant[tid]["allowed"] += 1
    tenants = []
    for tid, data in sorted(by_tenant.items(), key=lambda x: -x[1]["throttled"]):
        total = data["allowed"] + data["throttled"]
        tenants.append({"tenant_id": tid, "allowed": data["allowed"],
                        "throttled": data["throttled"],
                        "throttle_rate": round(data["throttled"] / max(total, 1) * 100, 1)})
    total_throttled = sum(t["throttled"] for t in tenants)
    total_allowed = sum(t["allowed"] for t in tenants)
    return {"tenants": tenants, "total_allowed": total_allowed,
            "total_throttled": total_throttled,
            "overall_rate": round(total_throttled / max(total_throttled + total_allowed, 1) * 100, 1)}
