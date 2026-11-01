from app.services.app_marketplace_app_canary_deployment import create_canary, adjust_traffic, evaluate_canary_health

def test_create():
    c = create_canary(app_id="a1", stable_version="1.0", canary_version="2.0")
    assert c["canary_pct"] == 5
    assert c["status"] == "active"

def test_create_invalid():
    c = create_canary(app_id="a1", stable_version="1.0", canary_version="2.0", initial_pct=80)
    assert c["error"]

def test_promote():
    c = {"app_id": "a1", "canary_pct": 50, "status": "active"}
    r = adjust_traffic(canary=c, new_pct=100)
    assert r["status"] == "promoted"

def test_rollback():
    c = {"app_id": "a1", "canary_pct": 10}
    r = adjust_traffic(canary=c, new_pct=0)
    assert r["status"] == "rolled_back"

def test_healthy():
    r = evaluate_canary_health(canary_metrics={"error_rate": 0.5, "p99_ms": 200},
                                stable_metrics={"error_rate": 0.4, "p99_ms": 180})
    assert r["healthy"]
    assert r["recommendation"] == "promote"

def test_degraded():
    r = evaluate_canary_health(canary_metrics={"error_rate": 5.0, "p99_ms": 200},
                                stable_metrics={"error_rate": 0.5, "p99_ms": 180})
    assert not r["healthy"]
    assert r["recommendation"] == "rollback"
