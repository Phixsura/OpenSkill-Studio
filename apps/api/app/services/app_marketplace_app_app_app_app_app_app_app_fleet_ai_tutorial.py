"""Fleet AI Tutorial Engine — track interactive AI learning experiences."""
from __future__ import annotations
def fleet_ai_tutorial(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    tutorials = sum(e.get("tutorials", 0) for e in engines)
    completions_24h = sum(e.get("completions_24h", 0) for e in engines)
    rating = round(sum(e.get("rating", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "tutorials": tutorials,
            "completions_24h": completions_24h, "rating": rating, "popular": rating > 4}
