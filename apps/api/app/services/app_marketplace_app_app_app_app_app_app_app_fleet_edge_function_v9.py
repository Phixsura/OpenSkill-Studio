"""Fleet Edge Function v9 — track edge-deployed serverless functions."""
from __future__ import annotations
def fleet_edge_function_v9(functions: list[dict]) -> dict:
    deployed = [f for f in functions if f.get("deployed")]
    invocations = sum(f.get("invocations_per_sec", 0) for f in functions)
    regions = len({f.get("region") for f in functions if f.get("region")})
    return {"functions": len(functions), "deployed": len(deployed), "invocations_per_sec": invocations,
            "regions": regions, "healthy": len(deployed) == len(functions)}
