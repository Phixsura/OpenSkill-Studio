from app.services.app_marketplace_app_automated_testing import run_test_pipeline

def test_all_pass():
    suites = [
        {"name": "Unit Tests", "passed": 50, "failed": 0, "skipped": 2, "duration_ms": 3000},
        {"name": "Integration", "passed": 20, "failed": 0, "skipped": 0, "duration_ms": 8000},
    ]
    r = run_test_pipeline(app_id="a1", test_suites=suites)
    assert r["all_passed"]
    assert r["publishable"]
    assert r["summary"]["total"] == 72

def test_with_failures():
    suites = [{"name": "Unit", "passed": 48, "failed": 2, "skipped": 0, "duration_ms": 3000}]
    r = run_test_pipeline(app_id="a1", test_suites=suites)
    assert not r["all_passed"]
    assert not r["publishable"]
    assert r["suites"][0]["status"] == "failed"
