"""Activity counter — track daily/weekly/monthly active users."""
from __future__ import annotations


def compute_active_users(events: list[dict]) -> dict:
    daily: set[str] = set()
    weekly: set[str] = set()
    monthly: set[str] = set()
    for e in events:
        uid = e.get("user_id", "")
        period = e.get("period", "daily")
        if period == "daily":
            daily.add(uid)
        elif period == "weekly":
            weekly.add(uid)
        elif period == "monthly":
            monthly.add(uid)
    # Users active daily are also weekly and monthly
    weekly |= daily
    monthly |= weekly
    dau = len(daily)
    wau = len(weekly)
    mau = len(monthly)
    stickiness = round(dau / max(mau, 1) * 100, 1)
    return {
        "dau": dau, "wau": wau, "mau": mau,
        "dau_display": f"{dau:,}", "wau_display": f"{wau:,}", "mau_display": f"{mau:,}",
        "stickiness": stickiness, "stickiness_display": f"{stickiness}%",
        "engagement": "high" if stickiness >= 20 else "medium" if stickiness >= 10 else "low",
    }
