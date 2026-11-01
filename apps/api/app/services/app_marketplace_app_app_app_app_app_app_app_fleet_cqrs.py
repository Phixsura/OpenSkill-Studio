"""Fleet CQRS — command/query responsibility segregation status."""
from __future__ import annotations
def fleet_cqrs_status(services: list[dict]) -> dict:
    using_cqrs = [s for s in services if s.get("cqrs_enabled", False)]
    read_replicas = sum(s.get("read_replicas", 0) for s in using_cqrs)
    return {"total": len(services), "cqrs_enabled": len(using_cqrs),
            "read_replicas": read_replicas, "adoption_pct": round(len(using_cqrs) / max(len(services), 1) * 100, 1)}
