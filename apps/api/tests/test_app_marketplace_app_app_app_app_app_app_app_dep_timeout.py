from app.services.app_marketplace_app_app_app_app_app_app_app_dep_timeout import calculate_chain_timeout, validate_timeouts

def test_chain():
    r = calculate_chain_timeout([
        {"service": "gateway", "timeout_ms": 100},
        {"service": "api", "timeout_ms": 200},
        {"service": "db", "timeout_ms": 50},
    ], buffer_pct=10)
    assert r["sum_ms"] == 350
    assert r["chain_timeout_ms"] == 385  # 350 + 35
    assert r["depth"] == 3

def test_validate():
    r = validate_timeouts(500, [
        {"timeout_ms": 200}, {"timeout_ms": 100}, {"timeout_ms": 300}
    ])
    assert not r["valid"]
    assert r["recommendation"] == "increase_parent"

    r2 = validate_timeouts(1000, [{"timeout_ms": 200}, {"timeout_ms": 300}])
    assert r2["valid"]
    assert r2["slack_ms"] == 500
