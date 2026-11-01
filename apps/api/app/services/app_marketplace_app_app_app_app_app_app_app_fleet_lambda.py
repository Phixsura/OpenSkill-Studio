"""Fleet AWS Lambda — track serverless function health."""
from __future__ import annotations
def fleet_lambda_status(functions: list[dict]) -> dict:
    active = [f for f in functions if f.get("state") == "Active"]
    total_invocations = sum(f.get("invocations_24h", 0) for f in functions)
    errors = sum(f.get("errors_24h", 0) for f in functions)
    cold_starts_pct = round(sum(f.get("cold_start_pct", 0) for f in functions) / max(len(functions), 1), 1)
    return {"functions": len(functions), "active": len(active), "invocations_24h": total_invocations,
            "errors_24h": errors, "cold_start_pct": cold_starts_pct, "healthy": errors == 0}
