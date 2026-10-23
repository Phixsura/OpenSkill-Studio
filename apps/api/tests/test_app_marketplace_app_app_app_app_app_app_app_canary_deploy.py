from app.services.app_marketplace_app_app_app_app_app_app_app_canary_deploy import (
    create_canary, evaluate_canary, advance_canary,
)

def test_canary_flow():
    c = create_canary("api", "2.0", "2.1", initial_pct=5.0)
    assert c["traffic_pct"] == 5.0
    e = evaluate_canary(c, {"error_rate": 0.5, "p99_latency_ms": 100},
                          {"error_rate": 0.6, "p99_latency_ms": 110})
    assert e["healthy"]
    assert e["action"] == "advance"
    advance_canary(c, 50)
    assert c["phase"] == "majority"
    e2 = evaluate_canary(c, {"error_rate": 0.5}, {"error_rate": 0.6})
    assert e2["action"] == "promote"

def test_rollback():
    c = create_canary("web", "1.0", "1.1")
    e = evaluate_canary(c, {"error_rate": 0.5, "p99_latency_ms": 100},
                          {"error_rate": 5.0, "p99_latency_ms": 500})
    assert not e["healthy"]
    assert e["action"] == "rollback"
