"""Alert dashboard — unified view of all active alerts."""
from __future__ import annotations


def build_alert_dashboard(alerts: list[dict]) -> dict:
    active = [a for a in alerts if a.get("status") == "firing"]
    resolved = [a for a in alerts if a.get("status") == "resolved"]
    by_sev: dict[str, int] = {}
    for a in active:
        sev = a.get("severity", "info")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    critical = by_sev.get("critical", 0)
    return {"active": len(active), "resolved": len(resolved), "total": len(alerts),
            "by_severity": by_sev, "critical_count": critical,
            "status": "critical" if critical > 0 else "warning" if active else "clear"}


def group_by_service(alerts: list[dict]) -> dict:
    by_svc: dict[str, list[dict]] = {}
    for a in alerts:
        svc = a.get("service", "unknown")
        by_svc.setdefault(svc, []).append(a)
    return {"services": {k: len(v) for k, v in by_svc.items()},
            "most_alerts": max(by_svc, key=lambda k: len(by_svc[k])) if by_svc else None}
