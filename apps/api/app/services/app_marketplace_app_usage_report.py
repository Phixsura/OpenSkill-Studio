"""Usage report — periodic usage summaries for app owners and org admins."""

from datetime import datetime, timezone


def generate_usage_report(*, app_id: str, period: str, metrics: dict) -> dict:
    return {
        "app_id": app_id, "period": period,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "api_calls": metrics.get("api_calls", 0),
            "unique_users": metrics.get("unique_users", 0),
            "avg_response_ms": metrics.get("avg_response_ms", 0),
            "error_count": metrics.get("error_count", 0),
            "uptime_pct": metrics.get("uptime_pct", 100),
        },
        "highlights": build_highlights(metrics),
    }


def build_highlights(metrics: dict) -> list[str]:
    highlights = []
    if metrics.get("api_calls", 0) > 10000:
        highlights.append(f"🔥 {metrics['api_calls']:,} API calls this period")
    if metrics.get("uptime_pct", 100) >= 99.9:
        highlights.append("✅ 99.9%+ uptime maintained")
    if metrics.get("error_count", 0) == 0:
        highlights.append("🎉 Zero errors!")
    if metrics.get("new_installs", 0) > 0:
        highlights.append(f"📥 {metrics['new_installs']} new installations")
    return highlights or ["No notable highlights this period"]


def compare_periods(*, current: dict, previous: dict) -> dict:
    changes = {}
    for key in ("api_calls", "unique_users", "error_count"):
        cur = current.get(key, 0)
        prev = previous.get(key, 0)
        if prev > 0:
            changes[key] = {"current": cur, "previous": prev,
                            "change_pct": round((cur - prev) / prev * 100, 1)}
        else:
            changes[key] = {"current": cur, "previous": prev, "change_pct": 0}
    return changes
