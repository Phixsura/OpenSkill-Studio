from app.services.app_marketplace_app_app_app_app_app_app_app_rc_eval import evaluate_rc

def test_promote():
    r = evaluate_rc({"version": "2.0-rc1", "tests_passing": True, "security_scan_clean": True,
                      "p99_ms": 100, "p99_target": 500, "error_rate_pct": 0.1,
                      "error_target": 1, "code_reviewed": True})
    assert r["verdict"] == "promote"
    assert r["passed"] == 5

def test_reject():
    r = evaluate_rc({"version": "2.0-rc2", "tests_passing": False, "security_scan_clean": False})
    assert r["verdict"] == "reject"

def test_hold():
    r = evaluate_rc({"version": "2.0-rc3", "tests_passing": True, "security_scan_clean": True,
                      "code_reviewed": True, "p99_ms": 800, "p99_target": 500})
    assert r["verdict"] == "hold"
