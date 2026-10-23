"""Date range picker — preset and custom date range options."""

from datetime import datetime, timedelta


PRESETS = {
    "today": {"label": "Today", "days": 0},
    "yesterday": {"label": "Yesterday", "days": 1},
    "7d": {"label": "Last 7 days", "days": 7},
    "30d": {"label": "Last 30 days", "days": 30},
    "90d": {"label": "Last 90 days", "days": 90},
    "ytd": {"label": "Year to date", "days": None},
    "all": {"label": "All time", "days": None},
}


def resolve_date_range(*, preset: str, now: str | None = None) -> dict:
    config = PRESETS.get(preset)
    if not config:
        return {"error": f"Unknown preset. Valid: {', '.join(sorted(PRESETS))}"}
    current = datetime.fromisoformat(now) if now else datetime.utcnow()
    if preset == "today":
        start = current.replace(hour=0, minute=0, second=0)
        end = current
    elif preset == "yesterday":
        yesterday = current - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = yesterday.replace(hour=23, minute=59, second=59)
    elif preset == "ytd":
        start = current.replace(month=1, day=1, hour=0, minute=0, second=0)
        end = current
    elif preset == "all":
        start = datetime(2020, 1, 1)
        end = current
    else:
        start = current - timedelta(days=config["days"])
        end = current
    return {"preset": preset, "label": config["label"],
            "start": start.isoformat(), "end": end.isoformat(),
            "days": (end - start).days}
