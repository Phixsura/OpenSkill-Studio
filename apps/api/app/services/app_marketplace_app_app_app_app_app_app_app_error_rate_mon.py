"""Error rate monitor — track and alert on error rate changes."""
from __future__ import annotations


def monitor_error_rate(services: list[dict]) -> dict:
    results = []
    alerts = []
    for s in services:
        total = s.get("requests", 0)
        errors = s.get("errors", 0)
        rate = round(errors / max(total, 1) * 100, 2)
        threshold = s.get("threshold_pct", 1.0)
        breaching = rate > threshold
        results.append({"service": s["name"], "rate": rate, "threshold": threshold,
                         "breaching": breaching, "requests": total, "errors": errors})
        if breaching:
            alerts.append(s["name"])
    return {"results": results, "total_services": len(results),
            "alerting": len(alerts), "alert_services": alerts,
            "all_ok": len(alerts) == 0}
