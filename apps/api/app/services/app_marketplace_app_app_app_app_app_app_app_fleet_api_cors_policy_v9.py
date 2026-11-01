"""Fleet API CORS Policy v9 — track CORS policy enforcement across origins."""
from __future__ import annotations
def fleet_api_cors_policy_v9(policies: list[dict]) -> dict:
    strict = [p for p in policies if p.get("strict")]
    origins = sum(p.get("allowed_origins", 0) for p in policies)
    preflight = sum(p.get("preflight_today", 0) for p in policies)
    return {"policies": len(policies), "strict": len(strict), "total_origins": origins,
            "preflight_today": preflight, "healthy": len(strict) == len(policies)}
