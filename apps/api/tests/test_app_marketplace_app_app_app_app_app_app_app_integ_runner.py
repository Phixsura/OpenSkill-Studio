from app.services.app_marketplace_app_app_app_app_app_app_app_integ_runner import run_suite, compare_runs

def test_suite():
    r = run_suite("api", [
        {"name": "login", "status": "passed", "duration_ms": 50},
        {"name": "signup", "status": "passed", "duration_ms": 80},
        {"name": "checkout", "status": "failed", "duration_ms": 200, "error": "timeout"},
    ])
    assert r["passed"] == 2
    assert r["failed"] == 1
    assert r["pass_rate"] == 67
    assert not r["success"]

def test_compare():
    prev = run_suite("s", [{"name": "a", "status": "passed"}, {"name": "b", "status": "failed"}])
    curr = run_suite("s", [{"name": "a", "status": "failed"}, {"name": "b", "status": "passed"}])
    r = compare_runs(curr, prev)
    assert "a" in r["new_failures"]
    assert "b" in r["fixed"]
    assert r["regression"]
