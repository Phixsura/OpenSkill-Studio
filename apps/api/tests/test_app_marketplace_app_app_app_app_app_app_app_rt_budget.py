from app.services.app_marketplace_app_app_app_app_app_app_app_rt_budget import track_budget

def test_within():
    r = track_budget("/api/users", 200, [
        {"name": "auth", "duration_ms": 10},
        {"name": "query", "duration_ms": 80},
        {"name": "serialize", "duration_ms": 5},
    ])
    assert not r["over_budget"]
    assert r["pct_used"] == 47.5
    assert r["remaining_ms"] == 105

def test_over():
    r = track_budget("/api/reports", 100, [
        {"name": "auth", "duration_ms": 10},
        {"name": "query", "duration_ms": 120},
    ])
    assert r["over_budget"]
    assert r["remaining_ms"] == 0
