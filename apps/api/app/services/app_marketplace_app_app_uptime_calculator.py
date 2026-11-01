"""Uptime calculator — SLA uptime percentage and downtime budget."""


def calculate_uptime(*, total_minutes: int, downtime_minutes: int) -> dict:
    uptime_min = total_minutes - downtime_minutes
    pct = round(uptime_min / max(total_minutes, 1) * 100, 4)
    nines = 0
    if pct >= 99.999:
        nines = 5
    elif pct >= 99.99:
        nines = 4
    elif pct >= 99.9:
        nines = 3
    elif pct >= 99:
        nines = 2
    return {"uptime_pct": pct, "downtime_minutes": downtime_minutes,
            "uptime_minutes": uptime_min, "nines": nines,
            "nines_label": f"{'9' * nines}s" if nines else "< 2 nines"}


def monthly_budget(*, sla_pct: float) -> dict:
    total = 30 * 24 * 60  # 43200 minutes
    allowed_down = round(total * (1 - sla_pct / 100), 2)
    return {"sla_pct": sla_pct, "total_minutes": total,
            "allowed_downtime_min": allowed_down,
            "allowed_downtime_display": f"{int(allowed_down)}m" if allowed_down < 60 else f"{allowed_down/60:.1f}h"}


def annual_budget(*, sla_pct: float) -> dict:
    total = 365 * 24 * 60  # 525600 minutes
    allowed_down = round(total * (1 - sla_pct / 100), 2)
    hours = allowed_down / 60
    return {"sla_pct": sla_pct, "allowed_downtime_hours": round(hours, 1),
            "allowed_downtime_min": allowed_down}
