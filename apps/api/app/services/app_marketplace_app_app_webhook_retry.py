"""Webhook retry — delivery retry with exponential backoff."""

from __future__ import annotations
import html
from datetime import datetime, timezone, timedelta


def plan_retries(*, max_attempts: int = 5, base_delay_s: int = 60) -> dict:
    schedule = []
    cumulative = 0
    for i in range(max_attempts):
        delay = base_delay_s * (2 ** i)
        cumulative += delay
        schedule.append({"attempt": i + 1, "delay_s": delay,
                          "delay_display": f"{delay}s" if delay < 3600 else f"{delay//3600}h",
                          "cumulative_s": cumulative})
    return {"schedule": schedule, "max_attempts": max_attempts,
            "total_window_s": cumulative,
            "total_window_display": f"{cumulative//3600}h {(cumulative%3600)//60}m"}


def build_delivery_report(*, deliveries: list[dict]) -> dict:
    items = []
    for d in deliveries:
        items.append({
            "attempt": d.get("attempt", 1),
            "status_code": d.get("status_code", 0),
            "success": 200 <= d.get("status_code", 0) < 300,
            "response_ms": d.get("response_ms", 0),
            "timestamp": d.get("timestamp", ""),
            "error": html.escape(d.get("error", "")),
        })
    final_success = items[-1]["success"] if items else False
    total_attempts = len(items)
    return {"deliveries": items, "total_attempts": total_attempts,
            "final_success": final_success,
            "status": "delivered" if final_success else "failed"}
