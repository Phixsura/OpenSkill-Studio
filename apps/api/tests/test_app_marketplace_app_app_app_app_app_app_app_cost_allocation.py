from app.services.app_marketplace_app_app_app_app_app_app_app_cost_allocation import allocate_costs

def test_costs():
    items = [
        {"team": "platform", "service": "compute", "cost": 5000},
        {"team": "platform", "service": "storage", "cost": 1200},
        {"team": "data", "service": "compute", "cost": 3000},
        {"team": "frontend", "service": "cdn", "cost": 800},
    ]
    r = allocate_costs(items)
    assert r["total"] == 10000
    assert r["top_spender"] == "platform"
    assert r["by_team"][0]["cost"] == 6200
    assert r["by_service"][0]["service"] == "compute"
    assert r["by_service"][0]["cost"] == 8000
