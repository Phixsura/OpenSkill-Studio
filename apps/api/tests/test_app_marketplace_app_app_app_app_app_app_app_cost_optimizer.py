from app.services.app_marketplace_app_app_app_app_app_app_app_cost_optimizer import analyze_cost_savings

def test_optimizer():
    resources = [
        {"name": "idle-server", "type": "compute", "monthly_cost": 500, "utilization_pct": 5},
        {"name": "web-server", "type": "compute", "monthly_cost": 300, "utilization_pct": 40},
        {"name": "db-primary", "type": "database", "monthly_cost": 800, "utilization_pct": 75, "reserved": False},
        {"name": "cache", "type": "cache", "monthly_cost": 50, "utilization_pct": 90},
    ]
    r = analyze_cost_savings(resources)
    assert r["count"] == 3
    assert r["potential_savings"] > 0
    assert r["recommendations"][0]["savings"] > r["recommendations"][-1]["savings"]
    assert r["savings_pct"] > 0
