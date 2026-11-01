"""Dependency SLA chain — calculate composite SLA from dependency chain."""
from __future__ import annotations


def calculate_chain_sla(services: list[dict]) -> dict:
    if not services:
        return {"composite_sla": 100, "services": 0}
    composite = 1.0
    chain = []
    for s in services:
        sla = s.get("sla_pct", 99.9) / 100
        composite *= sla
        chain.append({"service": s["name"], "sla_pct": s.get("sla_pct", 99.9)})
    composite_pct = round(composite * 100, 4)
    downtime_min_month = round((1 - composite) * 43200, 1)
    return {"composite_sla": composite_pct, "services": len(services),
            "chain": chain, "downtime_minutes_month": downtime_min_month,
            "meets_target": composite_pct >= 99.9}


def weakest_link(services: list[dict]) -> dict:
    if not services:
        return {"service": "", "sla_pct": 100}
    worst = min(services, key=lambda s: s.get("sla_pct", 100))
    return {"service": worst["name"], "sla_pct": worst.get("sla_pct", 100)}
