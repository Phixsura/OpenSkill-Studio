"""Gateway circuit analytics — track circuit breaker stats at the gateway."""
from __future__ import annotations
from collections import defaultdict


def gateway_circuit_stats(events: list[dict]) -> dict:
    by_backend: dict[str, dict] = defaultdict(lambda: {"trips": 0, "recoveries": 0, "requests_blocked": 0})
    for e in events:
        backend = e["backend"]
        if e["event"] == "trip":
            by_backend[backend]["trips"] += 1
        elif e["event"] == "recover":
            by_backend[backend]["recoveries"] += 1
        elif e["event"] == "blocked":
            by_backend[backend]["requests_blocked"] += 1
    results = []
    for backend, data in sorted(by_backend.items()):
        results.append({"backend": backend, **data})
    total_trips = sum(d["trips"] for d in by_backend.values())
    total_blocked = sum(d["requests_blocked"] for d in by_backend.values())
    return {"backends": results, "total_trips": total_trips,
            "total_blocked": total_blocked, "backends_affected": len(by_backend)}
