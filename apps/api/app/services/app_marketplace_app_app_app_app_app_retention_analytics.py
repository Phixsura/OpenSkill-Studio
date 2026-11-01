"""Retention analytics — cohort-based user retention analysis."""

from collections import defaultdict


def build_retention_cohorts(*, cohorts: list[dict]) -> dict:
    items = []
    for c in cohorts:
        week_retention = c.get("weekly_retention", [])
        items.append({
            "cohort": c.get("cohort", ""),
            "size": c.get("size", 0),
            "weekly_retention": week_retention,
            "week_1": week_retention[0] if len(week_retention) > 0 else 0,
            "week_4": week_retention[3] if len(week_retention) > 3 else 0,
        })
    avg_week1 = round(sum(c["week_1"] for c in items) / max(len(items), 1), 1)
    avg_week4 = round(sum(c["week_4"] for c in items) / max(len(items), 1), 1)
    return {"cohorts": items, "total_cohorts": len(items),
            "avg_week1_retention": avg_week1, "avg_week4_retention": avg_week4}
