"""Analytics dashboard — compile developer analytics overview."""

from datetime import datetime, timezone


def build_analytics_dashboard(*, app_id: str, installs: list[dict], events: list[dict],
                                 errors: list[dict], period_days: int = 30) -> dict:
    total_installs = len(installs)
    active_installs = sum(1 for i in installs if i.get("status") == "active")
    churn_rate = round((total_installs - active_installs) / max(total_installs, 1) * 100, 1)
    event_count = len(events)
    error_count = len(errors)
    error_rate = round(error_count / max(event_count, 1) * 100, 2)
    top_events = {}
    for e in events:
        t = e.get("event_type", "unknown")
        top_events[t] = top_events.get(t, 0) + 1
    sorted_events = sorted(top_events.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "app_id": app_id,
        "period_days": period_days,
        "installs": {"total": total_installs, "active": active_installs, "churn_rate": churn_rate},
        "events": {"total": event_count, "top": [{"type": t, "count": c} for t, c in sorted_events]},
        "errors": {"total": error_count, "rate": error_rate},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
