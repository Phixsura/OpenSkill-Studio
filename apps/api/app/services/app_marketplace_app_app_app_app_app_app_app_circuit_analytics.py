"""Circuit analytics — analyze circuit breaker patterns over time."""
from __future__ import annotations
from collections import defaultdict


def analyze_circuits(events: list[dict]) -> dict:
    by_service: dict[str, dict] = defaultdict(lambda: {"trips": 0, "recoveries": 0, "total_open_ms": 0})
    for e in events:
        svc = e["service"]
        if e["event"] == "trip":
            by_service[svc]["trips"] += 1
        elif e["event"] == "recover":
            by_service[svc]["recoveries"] += 1
            by_service[svc]["total_open_ms"] += e.get("open_duration_ms", 0)
    results = []
    for svc, data in sorted(by_service.items()):
        avg_open = round(data["total_open_ms"] / max(data["recoveries"], 1), 1)
        results.append({"service": svc, "trips": data["trips"],
                        "recoveries": data["recoveries"], "avg_open_ms": avg_open})
    flapping = [r for r in results if r["trips"] > 5]
    return {"services": results, "total_trips": sum(r["trips"] for r in results),
            "flapping_services": len(flapping)}


def circuit_mttr(events: list[dict]) -> dict:
    open_times: dict[str, float] = {}
    durations = []
    for e in events:
        svc = e["service"]
        if e["event"] == "trip":
            open_times[svc] = e.get("timestamp", 0)
        elif e["event"] == "recover" and svc in open_times:
            dur = e.get("timestamp", 0) - open_times[svc]
            durations.append(dur)
            del open_times[svc]
    if not durations:
        return {"mttr_ms": 0, "recoveries": 0}
    return {"mttr_ms": round(sum(durations) / len(durations), 1),
            "recoveries": len(durations), "min_ms": min(durations), "max_ms": max(durations)}
