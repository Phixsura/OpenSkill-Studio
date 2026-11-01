"""Timezone converter — convert timestamps between timezones for global teams."""
from __future__ import annotations

OFFSETS = {
    "UTC": 0, "EST": -5, "CST": -6, "MST": -7, "PST": -8,
    "CET": 1, "EET": 2, "IST": 5.5, "JST": 9, "AEST": 10,
    "GMT": 0, "BST": 1, "KST": 9, "SGT": 8, "HKT": 8,
}


def convert_hour(*, hour: int, from_tz: str, to_tz: str) -> dict:
    from_offset = OFFSETS.get(from_tz, 0)
    to_offset = OFFSETS.get(to_tz, 0)
    diff = to_offset - from_offset
    converted = (hour + diff) % 24
    day_change = "next_day" if hour + diff >= 24 else "prev_day" if hour + diff < 0 else "same_day"
    return {
        "from_hour": hour, "from_tz": from_tz,
        "to_hour": int(converted), "to_tz": to_tz,
        "offset_diff": diff, "day_change": day_change,
        "display": f"{int(converted):02d}:00 {to_tz}",
    }


def team_times(*, hour: int, from_tz: str, team_tzs: list[str]) -> list[dict]:
    return [convert_hour(hour=hour, from_tz=from_tz, to_tz=tz) for tz in team_tzs]


def list_timezones() -> list[dict]:
    return [{"tz": k, "offset": v, "display": f"UTC{'+' if v >= 0 else ''}{v}"} for k, v in sorted(OFFSETS.items(), key=lambda x: x[1])]
