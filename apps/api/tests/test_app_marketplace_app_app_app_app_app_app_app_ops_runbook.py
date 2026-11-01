from app.services.app_marketplace_app_app_app_app_app_app_app_ops_runbook import execute_runbook

def test_success():
    r = execute_runbook("restart-service", [
        {"name": "Stop service", "auto_success": True, "est_duration_ms": 500},
        {"name": "Clear cache", "auto_success": True, "est_duration_ms": 200},
        {"name": "Start service", "auto_success": True, "est_duration_ms": 1000},
    ])
    assert r["all_ok"]
    assert r["steps_executed"] == 3
    assert r["total_duration_ms"] == 1700

def test_failure():
    r = execute_runbook("migrate", [
        {"name": "Backup", "auto_success": True},
        {"name": "Migrate", "auto_success": False, "stop_on_failure": True},
        {"name": "Verify", "auto_success": True},
    ])
    assert not r["all_ok"]
    assert r["steps_executed"] == 2  # stopped at failure
