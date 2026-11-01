from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_health import post_deploy_check, should_rollback

def test_healthy():
    r = post_deploy_check([
        {"name": "http_200", "passed": True, "duration_ms": 50},
        {"name": "db_connected", "passed": True, "duration_ms": 10},
    ])
    assert r["healthy"]
    assert r["passed"] == 2

def test_unhealthy():
    r = post_deploy_check([
        {"name": "http_200", "passed": True, "duration_ms": 50},
        {"name": "db_connected", "passed": False, "duration_ms": 5000, "message": "timeout"},
    ])
    assert not r["healthy"]
    assert "db_connected" in r["failed_checks"]

def test_rollback():
    health = {"failed": 2}
    r = should_rollback(health, auto_rollback_threshold=1)
    assert r["rollback"]
    assert r["recommendation"] == "rollback"
