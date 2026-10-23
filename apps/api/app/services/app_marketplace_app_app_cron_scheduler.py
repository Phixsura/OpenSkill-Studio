"""Cron scheduler — cron expression parser and next-run calculator."""

import re
from datetime import datetime, timezone


CRON_FIELD_RE = re.compile(r"^(\*|(\d{1,2}(-\d{1,2})?(,\d{1,2}(-\d{1,2})?)*)(\/\d{1,2})?)$")


def validate_cron(*, expression: str) -> dict:
    parts = expression.strip().split()
    if len(parts) != 5:
        return {"valid": False, "errors": ["Must have exactly 5 fields (minute hour dom month dow)"]}
    labels = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 6)]
    errors = []
    fields = []
    for i, (part, label, (lo, hi)) in enumerate(zip(parts, labels, ranges)):
        if not CRON_FIELD_RE.match(part) and part != "*":
            errors.append(f"Invalid {label}: {part}")
        fields.append({"field": label, "value": part, "range": f"{lo}-{hi}"})
    return {"valid": len(errors) == 0, "errors": errors, "fields": fields,
            "expression": expression.strip()}


def describe_cron(*, expression: str) -> str:
    parts = expression.strip().split()
    if len(parts) != 5:
        return "Invalid cron expression"
    m, h, dom, mon, dow = parts
    desc = []
    if m == "0" and h == "*":
        desc.append("Every hour")
    elif m == "0" and h == "0":
        desc.append("Daily at midnight")
    elif h != "*" and m != "*":
        desc.append(f"At {h.zfill(2)}:{m.zfill(2)}")
    else:
        desc.append(f"At minute {m}" if m != "*" else "Every minute")
    if dow != "*":
        days = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat"}
        desc.append("on " + ",".join(days.get(d, d) for d in dow.split(",")))
    return " ".join(desc)
