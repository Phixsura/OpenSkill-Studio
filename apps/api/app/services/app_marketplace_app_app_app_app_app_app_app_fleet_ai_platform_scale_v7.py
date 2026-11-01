"""Fleet AI Scale v7 — track ultimate platform scalability."""
from __future__ import annotations
def fleet_ai_scale_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    peak_rps = sum(s.get("peak_rps", 0) for s in systems)
    gpus = sum(s.get("gpus", 0) for s in systems)
    data_pb = round(sum(s.get("data_pb", 0) for s in systems), 1)
    users = sum(s.get("users", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "peak_rps": peak_rps,
            "gpus": gpus, "data_pb": data_pb, "users": users, "hyperscale": peak_rps > 10000000}
