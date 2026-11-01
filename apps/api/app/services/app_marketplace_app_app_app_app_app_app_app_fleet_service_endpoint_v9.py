"""Fleet Service Endpoint v9 — track K8s service endpoint readiness."""
from __future__ import annotations
def fleet_service_endpoint_v9(endpoints: list[dict]) -> dict:
    ready = [e for e in endpoints if e.get("ready")]
    not_ready = [e for e in endpoints if not e.get("ready")]
    addresses = sum(e.get("addresses", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "ready": len(ready), "not_ready": len(not_ready),
            "total_addresses": addresses, "healthy": len(not_ready) == 0}
