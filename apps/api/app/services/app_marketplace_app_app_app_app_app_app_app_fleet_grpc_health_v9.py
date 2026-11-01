"""Fleet gRPC Health v9 — track gRPC service health and streaming."""
from __future__ import annotations
def fleet_grpc_health_v9(services: list[dict]) -> dict:
    serving = [s for s in services if s.get("status") == "SERVING"]
    not_serving = [s for s in services if s.get("status") == "NOT_SERVING"]
    streams_active = sum(s.get("active_streams", 0) for s in services)
    return {"services": len(services), "serving": len(serving), "not_serving": len(not_serving),
            "active_streams": streams_active, "healthy": len(not_serving) == 0}
