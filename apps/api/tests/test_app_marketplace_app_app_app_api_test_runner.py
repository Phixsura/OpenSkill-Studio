from app.services.app_marketplace_app_app_app_api_test_runner import run_api_tests

def test_run():
    tests = [
        {"name": "List apps", "method": "GET", "path": "/api/apps", "expected_status": 200, "actual_status": 200, "duration_ms": 45},
        {"name": "Create app", "method": "POST", "path": "/api/apps", "expected_status": 201, "actual_status": 201, "duration_ms": 120},
        {"name": "Bad auth", "method": "GET", "path": "/api/me", "expected_status": 200, "actual_status": 401, "duration_ms": 10},
    ]
    r = run_api_tests(tests=tests)
    assert r["total"] == 3
    assert r["passed"] == 2
    assert r["failed"] == 1
    assert not r["all_passed"]
    assert r["pass_rate"] == 66.7
