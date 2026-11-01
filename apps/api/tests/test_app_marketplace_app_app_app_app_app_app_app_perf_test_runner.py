from app.services.app_marketplace_app_app_app_app_app_app_app_perf_test_runner import run_perf_test, perf_test_summary

def test_pass():
    r = run_perf_test("api-load", 1000, 60,
                        {"actual_rps": 980, "p99_ms": 200, "error_rate_pct": 0.5, "latency_target_ms": 500})
    assert r["passed"]
    assert r["achieved_target"]

def test_fail():
    r = run_perf_test("api-stress", 5000, 60,
                        {"actual_rps": 3000, "p99_ms": 800, "error_rate_pct": 5, "latency_target_ms": 500})
    assert not r["passed"]

def test_summary():
    tests = [{"passed": True}, {"passed": True}, {"passed": False}]
    r = perf_test_summary(tests)
    assert r["pass_rate"] == 67
