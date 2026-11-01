"""API usage quota dashboard — aggregate quota usage across all tenants."""
from __future__ import annotations
from collections import defaultdict


def aggregate_quotas(tenants: list[dict]) -> dict:
    total_used = sum(t.get("used", 0) for t in tenants)
    total_limit = sum(t.get("limit", 0) for t in tenants)
    exceeded = [t for t in tenants if t.get("used", 0) >= t.get("limit", float("inf"))]
    warning = [t for t in tenants if 0.8 <= t.get("used", 0) / max(t.get("limit", 1), 1) < 1.0]
    return {"total_used": total_used, "total_limit": total_limit,
            "overall_pct": round(total_used / max(total_limit, 1) * 100, 1),
            "tenants": len(tenants), "exceeded": len(exceeded), "warning": len(warning)}


def top_consumers(tenants: list[dict], limit: int = 5) -> list[dict]:
    sorted_t = sorted(tenants, key=lambda t: -t.get("used", 0))[:limit]
    return [{"tenant": t["tenant_id"], "used": t["used"], "limit": t["limit"],
             "pct": round(t["used"] / max(t["limit"], 1) * 100, 1)} for t in sorted_t]
