from app.services.app_marketplace_app_app_app_app_app_app_app_infra_cost_opt import analyze_resources, projected_savings

def test_analyze():
    r = analyze_resources([
        {"name": "idle-server", "type": "compute", "monthly_cost": 100, "utilization_pct": 5},
        {"name": "web-server", "type": "compute", "monthly_cost": 200, "utilization_pct": 40},
        {"name": "db-server", "type": "database", "monthly_cost": 500, "utilization_pct": 85},
    ])
    assert r["total_cost"] == 800
    assert r["potential_savings"] > 0
    assert len(r["underutilized"]) == 1
    assert len(r["oversized"]) == 1
    assert r["recommendations"] == 2

def test_projected():
    r = projected_savings(150.0)
    assert r["annual"] == 1800.0
    assert r["display_annual"] == "$1,800.00"
