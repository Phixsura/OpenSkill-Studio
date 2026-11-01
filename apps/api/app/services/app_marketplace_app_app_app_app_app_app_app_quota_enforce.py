"""Service quota enforcement — enforce resource quotas per tenant."""
from __future__ import annotations


def enforce_quota(tenant_id: str, resource: str, current: float, limit: float) -> dict:
    pct = round(current / max(limit, 0.01) * 100, 1)
    exceeded = current >= limit
    warning = pct >= 80 and not exceeded
    remaining = max(0, round(limit - current, 2))
    return {"tenant_id": tenant_id, "resource": resource, "current": current,
            "limit": limit, "pct_used": pct, "exceeded": exceeded,
            "warning": warning, "remaining": remaining}


def quota_overview(quotas: list[dict]) -> dict:
    exceeded = sum(1 for q in quotas if q["exceeded"])
    warnings = sum(1 for q in quotas if q["warning"])
    return {"total": len(quotas), "exceeded": exceeded, "warnings": warnings,
            "healthy": len(quotas) - exceeded - warnings,
            "action_needed": exceeded > 0}
