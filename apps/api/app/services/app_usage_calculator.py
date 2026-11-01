"""Usage calculator — compute billing-relevant usage metrics."""

from datetime import UTC, datetime


def compute_usage_report(*, executions: int, webhook_deliveries: int, api_calls: int,
                         storage_bytes: int = 0, bandwidth_bytes: int = 0) -> dict:
    """Compute usage report for billing period."""
    return {
        "executions": executions,
        "webhook_deliveries": webhook_deliveries,
        "api_calls": api_calls,
        "storage_mb": round(storage_bytes / 1_048_576, 2),
        "bandwidth_mb": round(bandwidth_bytes / 1_048_576, 2),
        "total_operations": executions + webhook_deliveries + api_calls,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def estimate_cost(usage: dict, *, rates: dict | None = None) -> dict:
    """Estimate cost based on usage and rate table."""
    r = rates or {"execution": 0.001, "webhook": 0.0001, "api_call": 0.00005, "storage_mb": 0.05, "bandwidth_mb": 0.01}
    cost = (usage.get("executions", 0) * r["execution"] +
            usage.get("webhook_deliveries", 0) * r["webhook"] +
            usage.get("api_calls", 0) * r["api_call"] +
            usage.get("storage_mb", 0) * r["storage_mb"] +
            usage.get("bandwidth_mb", 0) * r["bandwidth_mb"])
    return {"estimated_cost_usd": round(cost, 4), "rates": r}
