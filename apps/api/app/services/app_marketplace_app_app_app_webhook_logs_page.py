"""App webhook logs page — complete webhook delivery log viewer."""

import html
from collections import defaultdict


def build_webhook_logs_page(*, deliveries: list[dict], page: int = 1,
                               page_size: int = 20) -> dict:
    total = len(deliveries)
    start = (page - 1) * page_size
    page_items = deliveries[start:start + page_size]
    items = []
    success = failed = 0
    for d in deliveries:
        ok = 200 <= d.get("status_code", 0) < 300
        if ok: success += 1
        else: failed += 1
    for d in page_items:
        ok = 200 <= d.get("status_code", 0) < 300
        items.append({
            "id": d.get("id", ""),
            "event": html.escape(d.get("event_type", "")),
            "url": html.escape(d.get("url", "")),
            "status_code": d.get("status_code", 0),
            "success": ok,
            "duration_ms": d.get("duration_ms", 0),
            "timestamp": d.get("timestamp", ""),
        })
    return {"deliveries": items, "total": total, "page": page,
            "total_pages": max(1, -(-total // page_size)),
            "success": success, "failed": failed,
            "success_rate": round(success / max(total, 1) * 100, 1)}
