"""Service availability calculator — calculate composite availability."""
from __future__ import annotations
import math


def serial_availability(services: list[float]) -> dict:
    composite = 1.0
    for a in services:
        composite *= a / 100
    composite_pct = round(composite * 100, 4)
    downtime_minutes_month = round((1 - composite) * 43200, 1)
    nines = -math.log10(max(1 - composite, 1e-10)) if composite < 1 else 10
    return {"composite_pct": composite_pct, "downtime_minutes_month": downtime_minutes_month,
            "nines": round(nines, 1), "components": len(services)}


def parallel_availability(services: list[float]) -> dict:
    fail_prob = 1.0
    for a in services:
        fail_prob *= (1 - a / 100)
    composite = round((1 - fail_prob) * 100, 6)
    return {"composite_pct": composite, "redundancy": len(services),
            "improvement": round(composite - max(services), 4)}


def compare_architectures(serial: list[float], parallel_groups: list[list[float]]) -> dict:
    serial_result = serial_availability(serial)
    parallel_avail = []
    for group in parallel_groups:
        parallel_avail.append(parallel_availability(group)["composite_pct"])
    combined = serial_availability(parallel_avail)
    return {"without_redundancy": serial_result["composite_pct"],
            "with_redundancy": combined["composite_pct"],
            "improvement_pct": round(combined["composite_pct"] - serial_result["composite_pct"], 4)}
