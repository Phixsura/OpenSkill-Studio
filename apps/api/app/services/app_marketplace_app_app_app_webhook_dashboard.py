"""App webhook dashboard — unified webhook management dashboard."""

import html
from datetime import datetime, timezone


def build_webhook_dashboard(*, endpoints: list[dict], recent_deliveries: list[dict],
                               period: str = "24h") -> dict:
    active_eps = sum(1 for e in endpoints if e.get("active"))
    total_deliveries = len(recent_deliveries)
    success = sum(1 for d in recent_deliveries if 200 <= d.get("status_code", 0) < 300)
    failed = total_deliveries - success
    success_rate = round(success / max(total_deliveries, 1) * 100, 1)
    return {
        "endpoints": [{"url": html.escape(e.get("url", "")), "active": e.get("active", True),
                         "events": e.get("events", [])} for e in endpoints],
        "endpoint_count": len(endpoints), "active_endpoints": active_eps,
        "deliveries": {"total": total_deliveries, "success": success,
                         "failed": failed, "success_rate": success_rate},
        "period": period, "health": "good" if success_rate >= 95 else "warning" if success_rate >= 80 else "critical",
    }
