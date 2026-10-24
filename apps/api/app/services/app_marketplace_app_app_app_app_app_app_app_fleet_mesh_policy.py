"""Fleet mesh policy — track service mesh access policies."""
from __future__ import annotations
def fleet_mesh_policy(services: list[dict]) -> dict:
    with_policy = [s for s in services if s.get("has_access_policy", False)]
    deny_all = [s for s in services if s.get("default_deny", False)]
    return {"total": len(services), "with_policy": len(with_policy),
            "default_deny": len(deny_all), "zero_trust": len(deny_all) == len(services)}
