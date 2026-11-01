"""Date range picker — preset and custom date range selection."""

from datetime import datetime, timedelta, timezone


PRESETS = {
    "today": 0, "yesterday": 1, "last_7d": 7, "last_30d": 30,
    "last_90d": 90, "last_year": 365,
}


def build_date_range(*, preset: str | None = None, start: str | None = None,
                      end: str | None = None) -> dict:
    now = datetime.now(timezone.utc)
    if preset and preset in PRESETS:
        days = PRESETS[preset]
        end_dt = now
        start_dt = now - timedelta(days=days)
        return {"start": start_dt.strftime("%Y-%m-%d"), "end": end_dt.strftime("%Y-%m-%d"),
                "preset": preset, "days": days + 1, "label": preset.replace("_", " ").title()}
    if start and end:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
        days = (e - s).days + 1
        return {"start": start, "end": end, "preset": None, "days": days, "label": f"{start} — {end}"}
    return {"start": now.strftime("%Y-%m-%d"), "end": now.strftime("%Y-%m-%d"),
            "preset": "today", "days": 1, "label": "Today"}


def list_presets() -> list[dict]:
    return [{"id": k, "label": k.replace("_", " ").title(), "days": v} for k, v in PRESETS.items()]
