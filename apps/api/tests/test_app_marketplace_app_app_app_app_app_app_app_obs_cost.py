from app.services.app_marketplace_app_app_app_app_app_app_app_obs_cost import calculate_obs_costs, suggest_optimizations

def test_costs():
    r = calculate_obs_costs(
        {"series": 5000, "cost_per_series": 0.01},
        {"gb_ingested": 100, "cost_per_gb": 0.50},
        {"spans_millions": 10, "cost_per_million": 2.00})
    assert r["metrics_cost"] == 50.0
    assert r["logs_cost"] == 50.0
    assert r["traces_cost"] == 20.0
    assert r["total_cost"] == 120.0

def test_suggestions():
    costs = {"total_cost": 2000, "breakdown_pct": {"metrics": 10, "logs": 60, "traces": 30}}
    s = suggest_optimizations(costs)
    assert len(s) >= 2
    assert any(x["area"] == "logs" for x in s)
