"""Fleet gRPC health — track gRPC service health."""
from __future__ import annotations
def fleet_grpc_health(services: list[dict]) -> dict:
    serving = [s for s in services if s.get("status") == "SERVING"]
    not_serving = [s for s in services if s.get("status") != "SERVING"]
    avg_latency = round(sum(s.get("avg_latency_ms", 0) for s in services) / max(len(services), 1), 1)
    return {"total": len(services), "serving": len(serving), "not_serving": len(not_serving),
            "avg_latency_ms": avg_latency, "healthy": len(not_serving) == 0}
