"""Metrics timeline — generate time-series data for app metrics."""

from datetime import UTC, datetime, timedelta


def generate_daily_timeline(*, days: int = 30, data_points: dict[str, int] | None = None) -> list[dict]:
    """Generate a daily timeline with optional data."""
    now = datetime.now(UTC)
    timeline = []
    dp = data_points or {}
    for i in range(days - 1, -1, -1):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        timeline.append({"date": date, "value": dp.get(date, 0)})
    return timeline


def aggregate_timeline(timelines: list[list[dict]]) -> list[dict]:
    """Aggregate multiple timelines by summing values per date."""
    totals: dict[str, int] = {}
    for tl in timelines:
        for point in tl:
            totals[point["date"]] = totals.get(point["date"], 0) + point["value"]
    return [{"date": d, "value": v} for d, v in sorted(totals.items())]
