"""App API key list — API key management with usage stats."""

import html
from datetime import datetime, timezone


def build_api_key_list(*, keys: list[dict]) -> dict:
    items = []
    active = 0
    for k in keys:
        is_active = not k.get("revoked", False)
        if is_active:
            active += 1
        items.append({
            "prefix": k.get("prefix", ""),
            "name": html.escape(k.get("name", "")),
            "scopes": k.get("scopes", []),
            "created_at": k.get("created_at", ""),
            "last_used": k.get("last_used"),
            "revoked": k.get("revoked", False),
            "requests_30d": k.get("requests_30d", 0),
        })
    return {"keys": items, "total": len(items), "active": active,
            "revoked": len(items) - active}


def get_key_usage(*, key_prefix: str, daily_counts: list[dict]) -> dict:
    total = sum(d.get("count", 0) for d in daily_counts)
    avg = round(total / max(len(daily_counts), 1))
    peak = max((d.get("count", 0) for d in daily_counts), default=0)
    return {"key_prefix": key_prefix, "total_requests": total,
            "avg_daily": avg, "peak_daily": peak,
            "days_tracked": len(daily_counts)}
