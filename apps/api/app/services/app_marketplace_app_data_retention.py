"""Data retention — manage data lifecycle and retention policies."""


DEFAULT_POLICIES = {
    "user_activity": {"retention_days": 365, "category": "analytics"},
    "api_logs": {"retention_days": 90, "category": "operations"},
    "crash_reports": {"retention_days": 180, "category": "debugging"},
    "audit_logs": {"retention_days": 730, "category": "compliance"},
    "session_data": {"retention_days": 30, "category": "operations"},
    "backup_data": {"retention_days": 90, "category": "infrastructure"},
}


def get_retention_policies(*, custom_overrides: dict | None = None) -> dict:
    policies = []
    overrides = custom_overrides or {}
    for key, default in DEFAULT_POLICIES.items():
        days = overrides.get(key, default["retention_days"])
        policies.append({
            "data_type": key,
            "retention_days": days,
            "category": default["category"],
            "is_custom": key in overrides,
        })
    return {"policies": policies, "total": len(policies)}


def estimate_storage_savings(*, current_size_gb: float, policies: list[dict],
                                avg_daily_growth_gb: float) -> dict:
    total_deletable = 0.0
    for p in policies:
        days = p.get("retention_days", 365)
        if days < 365:
            fraction = max(0, (365 - days) / 365)
            total_deletable += current_size_gb * fraction / len(policies)
    return {
        "current_size_gb": current_size_gb,
        "estimated_deletable_gb": round(total_deletable, 2),
        "estimated_monthly_savings_gb": round(avg_daily_growth_gb * 30 * 0.3, 2),
        "savings_pct": round(total_deletable / max(current_size_gb, 0.01) * 100, 1),
    }
