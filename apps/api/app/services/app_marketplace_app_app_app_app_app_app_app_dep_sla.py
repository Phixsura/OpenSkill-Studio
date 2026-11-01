"""Service dependency SLA — calculate composite SLA from dependencies."""
from __future__ import annotations


def calculate_composite_sla(dependencies: list[dict]) -> dict:
    if not dependencies:
        return {"composite_sla": 100, "weakest": None}
    composite = 100.0
    for d in dependencies:
        sla = d.get("sla_pct", 99.9)
        if d.get("serial", True):
            composite *= sla / 100
        else:
            # Parallel redundancy: 1 - (1-sla)^n for n replicas
            replicas = d.get("replicas", 1)
            single_failure = (100 - sla) / 100
            composite *= 1 - single_failure ** replicas
    composite = round(composite * 100, 4) if composite < 1 else round(composite, 4)
    weakest = min(dependencies, key=lambda d: d.get("sla_pct", 100))
    return {"composite_sla": composite, "dependencies": len(dependencies),
            "weakest": weakest.get("name", ""), "weakest_sla": weakest.get("sla_pct", 100)}


def nines_to_downtime(sla_pct: float, period_days: int = 30) -> dict:
    downtime_min = round((100 - sla_pct) / 100 * period_days * 24 * 60, 1)
    nines = 0
    val = sla_pct
    while val >= 90:
        nines += 1
        val = (val - 90) * 10
        if val < 0:
            break
    return {"sla_pct": sla_pct, "downtime_min": downtime_min,
            "nines": nines, "display": f"{sla_pct}% ({nines} nines)"}
