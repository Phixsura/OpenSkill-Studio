"""Cron expression parser — human-readable descriptions of cron schedules."""


MONTH_NAMES = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
DAY_NAMES = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}


def describe_cron(*, expression: str) -> dict:
    parts = expression.strip().split()
    if len(parts) != 5:
        return {"error": "Cron expression must have exactly 5 fields"}
    minute, hour, dom, month, dow = parts
    descriptions = []
    if minute == "*" and hour == "*":
        descriptions.append("Every minute")
    elif minute.startswith("*/"):
        descriptions.append(f"Every {minute[2:]} minutes")
    elif hour == "*":
        descriptions.append(f"At minute {minute} of every hour")
    else:
        descriptions.append(f"At {hour.zfill(2)}:{minute.zfill(2)}")
    if dow != "*":
        day_list = [DAY_NAMES.get(int(d), d) for d in dow.split(",") if d.isdigit()]
        if day_list:
            descriptions.append(f"on {', '.join(day_list)}")
    if dom != "*":
        descriptions.append(f"on day {dom}")
    if month != "*":
        month_list = [MONTH_NAMES.get(int(m), m) for m in month.split(",") if m.isdigit()]
        if month_list:
            descriptions.append(f"in {', '.join(month_list)}")
    return {
        "expression": expression,
        "description": " ".join(descriptions),
        "fields": {"minute": minute, "hour": hour, "day_of_month": dom,
                     "month": month, "day_of_week": dow},
    }
