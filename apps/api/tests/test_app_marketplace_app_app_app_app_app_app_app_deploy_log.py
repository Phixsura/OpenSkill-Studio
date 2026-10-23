from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_log import build_deploy_log

def test_deploy_log():
    r = build_deploy_log([
        {"name": "Build", "status": "success", "duration_ms": 5000, "output": "Built OK"},
        {"name": "Test", "status": "success", "duration_ms": 12000},
        {"name": "Deploy", "status": "success", "duration_ms": 8000},
    ])
    assert r["overall"] == "success"
    assert r["completed"] == 3
    assert r["total_duration_ms"] == 25000
    assert r["duration_display"] == "25.0s"

def test_failed():
    r = build_deploy_log([
        {"name": "Build", "status": "success", "duration_ms": 5000},
        {"name": "Test", "status": "failed", "duration_ms": 3000, "output": "2 tests failed"},
    ])
    assert r["overall"] == "failed"
    assert r["failed"] == 1
