"""Timezone helper — convert and display times across timezones."""

from datetime import datetime, timedelta


TIMEZONE_OFFSETS = {
    "UTC": 0, "US/Eastern": -5, "US/Central": -6, "US/Mountain": -7,
    "US/Pacific": -8, "Europe/London": 0, "Europe/Berlin": 1,
    "Europe/Moscow": 3, "Asia/Tokyo": 9, "Asia/Shanghai": 8,
    "Asia/Kolkata": 5.5, "Australia/Sydney": 11,
}


def convert_time(*, utc_time: str, target_tz: str) -> dict:
    offset = TIMEZONE_OFFSETS.get(target_tz)
    if offset is None:
        return {"error": f"Unknown timezone. Valid: {', '.join(sorted(TIMEZONE_OFFSETS))}"}
    try:
        dt = datetime.fromisoformat(utc_time)
    except ValueError:
        return {"error": "Invalid ISO datetime format"}
    converted = dt + timedelta(hours=offset)
    return {
        "utc": utc_time,
        "target_tz": target_tz,
        "offset_hours": offset,
        "converted": converted.isoformat(),
        "formatted": converted.strftime("%b %d, %Y at %I:%M %p"),
    }


def get_current_times(*, timezones: list[str]) -> dict:
    now = datetime.utcnow()
    times = []
    for tz in timezones:
        offset = TIMEZONE_OFFSETS.get(tz, 0)
        local = now + timedelta(hours=offset)
        times.append({"timezone": tz, "offset": offset,
                       "time": local.strftime("%H:%M"), "date": local.strftime("%Y-%m-%d")})
    return {"times": times, "utc_now": now.isoformat()}
