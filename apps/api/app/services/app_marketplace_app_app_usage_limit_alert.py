"""Usage limit alert — threshold-based usage limit notifications."""

import html


def check_usage_limits(*, limits: list[dict]) -> dict:
    alerts = []
    for l in limits:
        used = l.get("used", 0)
        limit = l.get("limit", 0)
        pct = round(used / max(limit, 1) * 100, 1) if limit > 0 else 0
        severity = "critical" if pct >= 100 else "warning" if pct >= 80 else "info" if pct >= 60 else "ok"
        if severity in ("critical", "warning"):
            alerts.append({
                "resource": html.escape(l.get("name", "")),
                "used": used, "limit": limit, "pct": pct,
                "severity": severity, "unit": l.get("unit", ""),
                "message": f"{html.escape(l.get('name', ''))} at {pct}% ({used:,}/{limit:,} {l.get('unit', '')})",
            })
    return {"alerts": alerts, "total_alerts": len(alerts),
            "has_critical": any(a["severity"] == "critical" for a in alerts),
            "all_ok": len(alerts) == 0}
