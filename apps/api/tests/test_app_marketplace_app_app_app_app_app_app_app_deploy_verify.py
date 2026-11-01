from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_verify import verify_deployment

def test_success():
    r = verify_deployment([
        {"name": "health_check", "status": "pass", "duration_ms": 50},
        {"name": "smoke_test", "status": "pass", "duration_ms": 200},
    ])
    assert r["success"]
    assert r["verdict"] == "deploy_verified"

def test_failure():
    r = verify_deployment([
        {"name": "health_check", "status": "pass", "duration_ms": 50},
        {"name": "smoke_test", "status": "fail", "duration_ms": 5000, "message": "timeout"},
    ])
    assert not r["success"]
    assert r["failed"] == 1
