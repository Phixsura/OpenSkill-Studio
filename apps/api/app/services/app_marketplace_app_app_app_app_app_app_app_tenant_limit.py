"""Tenant usage limiter — enforce usage limits per tenant."""
from __future__ import annotations


def check_limit(tenant_id: str, resource: str, current: float, limit: float) -> dict:
    pct = round(current / max(limit, 0.01) * 100, 1)
    exceeded = current >= limit
    warning = pct >= 80 and not exceeded
    return {"tenant_id": tenant_id, "resource": resource, "current": current,
            "limit": limit, "pct": pct, "exceeded": exceeded, "warning": warning,
            "remaining": round(max(0, limit - current), 2)}


def tenant_limits_overview(checks: list[dict]) -> dict:
    exceeded = sum(1 for c in checks if c["exceeded"])
    warnings = sum(1 for c in checks if c["warning"])
    return {"total_checks": len(checks), "exceeded": exceeded, "warnings": warnings,
            "healthy": len(checks) - exceeded - warnings,
            "action_needed": exceeded > 0}
