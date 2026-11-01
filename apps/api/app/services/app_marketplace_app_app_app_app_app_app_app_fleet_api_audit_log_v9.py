"""Fleet API Audit Log v9 — track API access audit logging."""
from __future__ import annotations
def fleet_api_audit_log_v9(logs: list[dict]) -> dict:
    entries = sum(l.get("entries_today", 0) for l in logs)
    sensitive_access = sum(l.get("sensitive_access", 0) for l in logs)
    retention_days = min((l.get("retention_days", 365) for l in logs), default=365)
    return {"log_sources": len(logs), "entries_today": entries, "sensitive_access": sensitive_access,
            "min_retention_days": retention_days, "healthy": retention_days >= 90}
