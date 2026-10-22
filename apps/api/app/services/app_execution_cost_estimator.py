"""Execution cost estimator — estimate costs for sandbox executions."""


def estimate_execution_cost(*, memory_mb: int, duration_seconds: float, tier: str = "standard") -> dict:
    rates = {"free": 0, "standard": 0.00001, "premium": 0.000008, "enterprise": 0.000005}
    rate = rates.get(tier, rates["standard"])
    # Cost = memory_gb * duration_seconds * rate
    memory_gb = memory_mb / 1024
    cost = round(memory_gb * duration_seconds * rate, 6)
    return {"cost_usd": cost, "memory_mb": memory_mb, "duration_s": duration_seconds, "tier": tier, "rate": rate}


def estimate_monthly_cost(*, avg_executions_per_day: int, avg_memory_mb: int, avg_duration_s: float, tier: str = "standard") -> dict:
    daily = estimate_execution_cost(memory_mb=avg_memory_mb, duration_seconds=avg_duration_s, tier=tier)
    monthly = round(daily["cost_usd"] * avg_executions_per_day * 30, 4)
    return {"monthly_cost_usd": monthly, "daily_executions": avg_executions_per_day, "per_execution_usd": daily["cost_usd"]}
