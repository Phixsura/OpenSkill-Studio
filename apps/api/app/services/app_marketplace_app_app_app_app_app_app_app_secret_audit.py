"""Secrets rotation auditor — audit secret age and rotation compliance."""
from __future__ import annotations
import time


def audit_secrets(secrets_list: list[dict], *, max_age_days: int = 90,
                   now: float | None = None) -> dict:
    ts = now if now is not None else time.time()
    results = []
    compliant = 0
    for s in secrets_list:
        age_days = round((ts - s.get("created_at", ts)) / 86400, 1)
        overdue = age_days > max_age_days
        days_until = round(max_age_days - age_days, 1)
        status = "overdue" if overdue else "warning" if days_until <= 14 else "ok"
        if not overdue:
            compliant += 1
        results.append({"name": s["name"], "age_days": age_days,
                         "days_until_rotation": max(0, days_until),
                         "status": status, "last_rotated": s.get("last_rotated", "never")})
    total = len(secrets_list)
    pct = round(compliant / max(total, 1) * 100)
    return {"total": total, "compliant": compliant, "non_compliant": total - compliant,
            "compliance_pct": pct, "max_age_days": max_age_days,
            "results": sorted(results, key=lambda r: -r["age_days"])}
