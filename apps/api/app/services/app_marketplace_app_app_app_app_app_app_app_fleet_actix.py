"""Fleet Actix — track Rust web framework health."""
from __future__ import annotations
def fleet_actix_status(services: list[dict]) -> dict:
    running = [s for s in services if s.get("running", True)]
    total_rps = sum(s.get("rps", 0) for s in services)
    p99_ms = round(sum(s.get("p99_ms", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "running": len(running), "rps": total_rps,
            "p99_ms": p99_ms, "blazing_fast": p99_ms < 5}
