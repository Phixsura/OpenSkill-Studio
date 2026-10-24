from app.services.app_marketplace_app_diagnostics import run_diagnostics, get_standard_checks

def test_all_pass():
    r = run_diagnostics(app_id="a1", checks={"manifest": True, "endpoints": True, "auth": True})
    assert r["health"] == "healthy"
    assert r["passed"] == 3

def test_some_fail():
    r = run_diagnostics(app_id="a1", checks={"manifest": True, "endpoints": False})
    assert r["health"] == "unhealthy"
    assert r["failed"] == 1

def test_standard_checks():
    checks = get_standard_checks()
    assert len(checks) == 8
    assert "manifest_valid" in checks
