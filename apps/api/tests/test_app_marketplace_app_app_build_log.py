from app.services.app_marketplace_app_app_build_log import parse_build_log

def test_success():
    steps = [
        {"name": "Install", "type": "install", "status": "success", "duration_ms": 5000},
        {"name": "Build", "type": "build", "status": "success", "duration_ms": 12000},
        {"name": "Test", "type": "test", "status": "success", "duration_ms": 8000},
    ]
    r = parse_build_log(steps=steps)
    assert r["overall"] == "success"
    assert r["total_steps"] == 3
    assert r["total_ms"] == 25000

def test_failure():
    steps = [
        {"name": "Install", "status": "success", "duration_ms": 3000},
        {"name": "Test", "type": "test", "status": "failed", "duration_ms": 1500},
    ]
    r = parse_build_log(steps=steps)
    assert r["overall"] == "failed"
    assert r["failed_step"] == "Test"
