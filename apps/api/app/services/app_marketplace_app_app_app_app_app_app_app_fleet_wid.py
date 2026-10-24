"""Fleet workload identity — track workload identity adoption."""
from __future__ import annotations
def fleet_workload_identity(services: list[dict]) -> dict:
    using_wi = [s for s in services if s.get("workload_identity", False)]
    using_keys = [s for s in services if s.get("uses_sa_keys", False)]
    return {"total": len(services), "workload_identity": len(using_wi),
            "sa_keys": len(using_keys), "modern": len(using_keys) == 0}
