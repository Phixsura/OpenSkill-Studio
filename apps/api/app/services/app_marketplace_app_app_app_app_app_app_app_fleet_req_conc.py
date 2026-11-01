"""Fleet request concurrency — track concurrent request levels."""
from __future__ import annotations
def fleet_request_concurrency(services: list[dict]) -> dict:
    total = sum(s.get("concurrent", 0) for s in services)
    max_conc = max((s.get("concurrent", 0) for s in services), default=0)
    cap = sum(s.get("max_concurrent", 1) for s in services)
    pct = round(total / max(cap, 1) * 100, 1)
    return {"total_concurrent": total, "max_single": max_conc, "capacity": cap, "util_pct": pct, "pressure": pct > 80}
