from app.services.app_marketplace_app_app_app_app_app_app_app_latency_budget import allocate_budget, check_budget

def test_allocate():
    r = allocate_budget(200, [
        {"name": "auth", "budget_ms": 20},
        {"name": "business_logic", "budget_ms": 100},
        {"name": "database", "budget_ms": 50},
    ])
    assert r["remaining_ms"] == 30
    assert not r["fully_allocated"]

def test_within():
    r = check_budget("/api/users", 200, 150)
    assert r["within_budget"]
    assert r["overshoot_ms"] == 0

def test_over():
    r = check_budget("/api/orders", 100, 180)
    assert not r["within_budget"]
    assert r["overshoot_ms"] == 80
