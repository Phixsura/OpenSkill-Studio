from app.services.app_marketplace_app_app_app_app_app_app_app_ep_error_budget import endpoint_error_budget, fleet_error_budgets

def test_within():
    r = endpoint_error_budget("/api/users", 100000, 50, 99.9)
    assert r["budget"] == 100
    assert not r["exhausted"]
    assert r["remaining"] == 50

def test_exhausted():
    r = endpoint_error_budget("/api/orders", 10000, 20, 99.9)
    assert r["exhausted"]

def test_fleet():
    r = fleet_error_budgets([
        {"endpoint": "/a", "total": 100000, "failed": 50},
        {"endpoint": "/b", "total": 10000, "failed": 20},
    ])
    assert r["exhausted"] == 1
    assert not r["all_within_budget"]
