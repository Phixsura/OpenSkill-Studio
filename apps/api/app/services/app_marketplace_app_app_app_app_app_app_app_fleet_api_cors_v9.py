"""Fleet API CORS v9 — track CORS policy enforcement across APIs."""
from __future__ import annotations
def fleet_api_cors_v9(policies: list[dict]) -> dict:
    configured = [p for p in policies if p.get("cors_configured")]
    wildcard = [p for p in policies if p.get("allow_origin") == "*"]
    preflight = sum(p.get("preflight_requests", 0) for p in policies)
    return {"policies": len(policies), "configured": len(configured), "wildcard_origins": len(wildcard),
            "preflight_requests": preflight, "healthy": len(wildcard) == 0}
