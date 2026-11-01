"""Fleet AI Cost — track AI/ML infrastructure spending."""
from __future__ import annotations
def fleet_ai_cost(services: list[dict]) -> dict:
    total_cost = sum(s.get("monthly_cost", 0) for s in services)
    gpu_cost = sum(s.get("gpu_cost", 0) for s in services)
    inference_cost = sum(s.get("inference_cost", 0) for s in services)
    savings = sum(s.get("savings_available", 0) for s in services)
    return {"total_monthly": round(total_cost, 2), "gpu_cost": round(gpu_cost, 2),
            "inference_cost": round(inference_cost, 2), "savings_available": round(savings, 2),
            "optimized": savings < total_cost * 0.1}
