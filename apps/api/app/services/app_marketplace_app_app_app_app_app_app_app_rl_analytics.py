"""Rate limit analytics — analyze rate limiting effectiveness."""
from __future__ import annotations
from collections import defaultdict


def analyze_rate_limits(events: list[dict]) -> dict:
    by_tenant: dict[str, dict] = defaultdict(lambda: {"allowed": 0, "denied": 0})
    for e in events:
        tid = e.get("tenant_id", "unknown")
        if e.get("allowed"):
            by_tenant[tid]["allowed"] += 1
        else:
            by_tenant[tid]["denied"] += 1
    tenants = []
    for tid, data in sorted(by_tenant.items(), key=lambda x: -x[1]["denied"]):
        total = data["allowed"] + data["denied"]
        deny_rate = round(data["denied"] / max(total, 1) * 100, 1)
        tenants.append({"tenant_id": tid, "allowed": data["allowed"],
                        "denied": data["denied"], "deny_rate": deny_rate})
    total_denied = sum(t["denied"] for t in tenants)
    total_allowed = sum(t["allowed"] for t in tenants)
    overall_rate = round(total_denied / max(total_denied + total_allowed, 1) * 100, 1)
    return {"tenants": tenants, "total_allowed": total_allowed,
            "total_denied": total_denied, "overall_deny_rate": overall_rate}
