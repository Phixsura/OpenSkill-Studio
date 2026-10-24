from app.services.app_marketplace_app_app_app_app_app_app_app_timeout_calc import calculate_timeout, timeout_summary

def test_timeout():
    r = calculate_timeout([
        {"name": "auth", "p99_ms": 50, "timeout_ms": 100},
        {"name": "db", "p99_ms": 150, "timeout_ms": 300},
    ])
    assert r["chain_p99_ms"] == 200
    assert r["recommended_timeout_ms"] == 240
    assert not r["over_budget"]

def test_summary():
    chains = [{"over_budget": False}, {"over_budget": True}]
    r = timeout_summary(chains)
    assert r["over_budget"] == 1
    assert not r["all_ok"]
