"""Webhook log — delivery attempt tracking with status."""

import html
from datetime import datetime, timezone


def build_webhook_log(*, deliveries: list[dict]) -> dict:
    items = []
    success = failed = 0
    for d in deliveries:
        status = d.get("status_code", 0)
        ok = 200 <= status < 300
        if ok:
            success += 1
        else:
            failed += 1
        items.append({
            "id": d["id"],
            "event": html.escape(d.get("event", "")),
            "url": html.escape(d.get("url", "")),
            "status_code": status,
            "success": ok,
            "duration_ms": d.get("duration_ms", 0),
            "timestamp": d.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "attempt": d.get("attempt", 1),
        })
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    rate = round(success / len(items) * 100, 1) if items else 0
    return {"deliveries": items, "total": len(items),
            "success": success, "failed": failed, "success_rate": rate}
