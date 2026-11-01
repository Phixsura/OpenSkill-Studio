"""Fleet Serverless Function v9 — track FaaS invocations and cold starts."""
from __future__ import annotations
def fleet_serverless_fn_v9(functions: list[dict]) -> dict:
    invocations = sum(f.get("invocations_per_min", 0) for f in functions)
    cold_starts = sum(f.get("cold_starts", 0) for f in functions)
    errors = sum(f.get("errors", 0) for f in functions)
    avg_duration = sum(f.get("avg_ms", 0) for f in functions) / len(functions) if functions else 0
    return {"functions": len(functions), "invocations_per_min": invocations,
            "cold_starts": cold_starts, "errors": errors, "avg_ms": round(avg_duration, 1),
            "healthy": errors == 0}
