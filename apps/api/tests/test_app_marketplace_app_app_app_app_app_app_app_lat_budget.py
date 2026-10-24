from app.services.app_marketplace_app_app_app_app_app_app_app_lat_budget import allocate_latency_budget

def test_budget():
    r = allocate_latency_budget("/api/users", 500, [
        {"name": "auth", "budget_ms": 50, "actual_ms": 30},
        {"name": "db_query", "budget_ms": 200, "actual_ms": 150},
        {"name": "serialize", "budget_ms": 50, "actual_ms": 40},
    ])
    assert r["allocated_ms"] == 300
    assert r["remaining_ms"] == 200
    assert not r["over_budget"]

def test_over():
    r = allocate_latency_budget("/api/slow", 100, [
        {"name": "db", "budget_ms": 50, "actual_ms": 200},
    ])
    assert r["over_budget"]
