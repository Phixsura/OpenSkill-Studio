from app.services.app_marketplace_app_app_app_app_app_app_app_health_scheduler import create_check, evaluate_check, summarize_checks

def test_check():
    c = create_check(name="API", url="https://api.example.com/health", interval="5m")
    assert c["interval_sec"] == 300
    r = evaluate_check(c, status_code=200, latency_ms=150)
    assert r["healthy"]

def test_failure():
    c = create_check(name="DB", url="https://db/health")
    r = evaluate_check(c, status_code=500, latency_ms=100)
    assert not r["healthy"]
    assert r["reason"] == "status_mismatch"

def test_summary():
    results = [{"healthy": True}, {"healthy": True}, {"healthy": False}]
    s = summarize_checks(results)
    assert s["healthy"] == 2
    assert not s["all_healthy"]
