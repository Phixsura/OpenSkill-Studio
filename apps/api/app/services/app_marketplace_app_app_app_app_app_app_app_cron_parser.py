"""Cron expression parser — parse and describe cron schedules."""
from __future__ import annotations

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
PRESETS = {
    "@yearly": "0 0 1 1 *", "@monthly": "0 0 1 * *", "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *", "@hourly": "0 * * * *",
}


def parse_cron(expr: str) -> dict:
    resolved = PRESETS.get(expr.strip(), expr.strip())
    parts = resolved.split()
    if len(parts) != 5:
        return {"valid": False, "error": f"expected 5 fields, got {len(parts)}"}
    fields = {}
    for i, name in enumerate(FIELD_NAMES):
        fields[name] = parts[i]
    return {"valid": True, "expression": resolved, "fields": fields,
            "is_preset": expr.strip() in PRESETS}


def describe_cron(expr: str) -> str:
    r = parse_cron(expr)
    if not r["valid"]:
        return r["error"]
    f = r["fields"]
    parts = []
    if f["minute"] == "0" and f["hour"] == "0":
        parts.append("At midnight")
    elif f["minute"] == "0" and f["hour"] != "*":
        parts.append(f"At {f['hour']}:00")
    elif f["minute"] != "*":
        h = f["hour"] if f["hour"] != "*" else "every hour"
        parts.append(f"At minute {f['minute']} of {h}")
    else:
        parts.append("Every minute")
    if f["day_of_month"] != "*":
        parts.append(f"on day {f['day_of_month']}")
    if f["month"] != "*":
        parts.append(f"in month {f['month']}")
    if f["day_of_week"] != "*":
        parts.append(f"on weekday {f['day_of_week']}")
    return " ".join(parts)
