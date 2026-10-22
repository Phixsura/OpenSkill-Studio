from app.services.app_execution_cost_estimator import estimate_execution_cost, estimate_monthly_cost

def test_single():
    c = estimate_execution_cost(memory_mb=256, duration_seconds=30)
    assert c["cost_usd"] >= 0

def test_free_tier():
    c = estimate_execution_cost(memory_mb=128, duration_seconds=10, tier="free")
    assert c["cost_usd"] == 0

def test_enterprise_cheaper():
    std = estimate_execution_cost(memory_mb=256, duration_seconds=30, tier="standard")
    ent = estimate_execution_cost(memory_mb=256, duration_seconds=30, tier="enterprise")
    assert ent["cost_usd"] <= std["cost_usd"]

def test_monthly():
    m = estimate_monthly_cost(avg_executions_per_day=100, avg_memory_mb=256, avg_duration_s=30)
    assert m["monthly_cost_usd"] >= 0
    assert m["daily_executions"] == 100
