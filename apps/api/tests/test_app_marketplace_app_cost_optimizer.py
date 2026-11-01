from app.services.app_marketplace_app_cost_optimizer import analyze_costs

def test_optimize():
    resources = [
        {"name": "API Server", "monthly_cost": 100, "utilization_pct": 15},
        {"name": "Database", "monthly_cost": 200, "utilization_pct": 80, "reserved": True},
        {"name": "Cache", "monthly_cost": 50, "utilization_pct": 40},
    ]
    r = analyze_costs(resources=resources)
    assert r["total_monthly_cost"] == 350
    assert r["total_potential_savings"] > 0
    assert any(rec["type"] == "downsize" for rec in r["recommendations"])

def test_no_savings():
    resources = [{"name": "App", "monthly_cost": 10, "utilization_pct": 90}]
    r = analyze_costs(resources=resources)
    assert r["total_potential_savings"] == 0
    assert len(r["recommendations"]) == 0
