from app.services.app_marketplace_app_app_app_app_app_app_app_canary_deploy import CanaryController

def test_canary_promote():
    c = CanaryController()
    c.start_canary(app_id="myapp", version="2.0", target_pct=50, step_pct=50)
    r = c.check_health("myapp", success_rate=0.999, latency_p99=150)
    assert r["action"] == "promote"
    assert r["traffic_pct"] == 100
    s = c.status("myapp")
    assert s["phase"] == "promoted"

def test_canary_rollback():
    c = CanaryController()
    c.start_canary(app_id="myapp", version="2.0", target_pct=10, step_pct=10)
    r = c.check_health("myapp", success_rate=0.95, latency_p99=500)
    assert r["action"] == "rollback"
    s = c.status("myapp")
    assert s["phase"] == "rollback"
    assert s["traffic_pct"] == 0
