"""Install count chart — daily/weekly/monthly install data for visualization."""

from collections import defaultdict


def aggregate_daily_installs(*, installs: list[dict], days: int = 30) -> list[dict]:
    by_day = defaultdict(int)
    for inst in installs:
        day = inst.get("installed_at", "")[:10]
        if day:
            by_day[day] += 1
    sorted_days = sorted(by_day.items())[-days:]
    return [{"date": d, "count": c} for d, c in sorted_days]


def compute_install_growth(*, daily_data: list[dict]) -> dict:
    if len(daily_data) < 2:
        return {"growth_pct": 0, "trend": "stable"}
    mid = len(daily_data) // 2
    first_half = sum(d["count"] for d in daily_data[:mid])
    second_half = sum(d["count"] for d in daily_data[mid:])
    if first_half == 0:
        return {"growth_pct": 100 if second_half > 0 else 0, "trend": "up" if second_half > 0 else "stable"}
    pct = round((second_half - first_half) / first_half * 100, 1)
    return {"growth_pct": pct, "trend": "up" if pct > 10 else "down" if pct < -10 else "stable",
            "first_half_total": first_half, "second_half_total": second_half}


def get_peak_install_day(*, daily_data: list[dict]) -> dict | None:
    if not daily_data:
        return None
    peak = max(daily_data, key=lambda d: d["count"])
    return {"date": peak["date"], "count": peak["count"]}
