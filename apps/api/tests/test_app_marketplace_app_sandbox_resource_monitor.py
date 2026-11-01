from app.services.app_marketplace_app_sandbox_resource_monitor import get_resource_snapshot, check_resource_limits

def test_snapshot():
    r = get_resource_snapshot(app_id="a1", sandbox_id="sb1")
    assert r["status"] == "running"
    assert r["cpu"]["usage_pct"] == 42.5
    assert r["memory"]["limit_mb"] == 512

def test_healthy():
    snap = get_resource_snapshot(app_id="a1", sandbox_id="sb1")
    r = check_resource_limits(snapshot=snap)
    assert r["healthy"]

def test_alerts():
    snap = {"cpu": {"usage_pct": 95}, "memory": {"usage_pct": 92},
            "disk": {"usage_pct": 50}, "network": {"connections": 10, "limit_connections": 50}}
    r = check_resource_limits(snapshot=snap)
    assert r["alert_count"] == 2
    assert not r["healthy"]
