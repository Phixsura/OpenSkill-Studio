"""Fleet SageMaker — track ML platform health."""
from __future__ import annotations
def fleet_sagemaker_status(endpoints: list[dict]) -> dict:
    in_service = [e for e in endpoints if e.get("status") == "InService"]
    total_instances = sum(e.get("instances", 0) for e in endpoints)
    invocations_24h = sum(e.get("invocations_24h", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "in_service": len(in_service), "instances": total_instances,
            "invocations_24h": invocations_24h, "all_serving": len(in_service) == len(endpoints)}
