"""Storage usage tracker — track storage consumption per tenant/service."""
from __future__ import annotations
from collections import defaultdict


def analyze_storage(resources: list[dict]) -> dict:
    by_type: dict[str, float] = defaultdict(float)
    by_tenant: dict[str, float] = defaultdict(float)
    for r in resources:
        by_type[r.get("type", "other")] += r.get("size_gb", 0)
        by_tenant[r.get("tenant", "shared")] += r.get("size_gb", 0)
    total = sum(by_type.values())
    return {"total_gb": round(total, 2),
            "by_type": {k: round(v, 2) for k, v in sorted(by_type.items(), key=lambda x: -x[1])},
            "by_tenant": {k: round(v, 2) for k, v in sorted(by_tenant.items(), key=lambda x: -x[1])},
            "resources": len(resources)}


def storage_forecast(current_gb: float, growth_rate_gb_per_month: float, limit_gb: float) -> dict:
    months_until_full = round((limit_gb - current_gb) / max(growth_rate_gb_per_month, 0.01))
    pct_used = round(current_gb / max(limit_gb, 0.01) * 100, 1)
    return {"current_gb": current_gb, "limit_gb": limit_gb, "pct_used": pct_used,
            "growth_rate": growth_rate_gb_per_month,
            "months_until_full": max(0, months_until_full),
            "action_needed": pct_used > 80}
