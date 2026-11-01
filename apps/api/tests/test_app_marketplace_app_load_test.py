from app.services.app_marketplace_app_load_test import run_load_test

def test_pass():
    r = run_load_test(app_id="a1", endpoint="/api/apps", concurrent_users=50, duration_sec=30, rps=20)
    assert r["verdict"] == "pass"
    assert r["results"]["total_requests"] == 600
    assert r["results"]["error_rate"] < 1

def test_high_load():
    r = run_load_test(app_id="a1", endpoint="/api/search", concurrent_users=5000)
    assert r["verdict"] in ("warning", "fail")

def test_too_many():
    r = run_load_test(app_id="a1", endpoint="/api", concurrent_users=50000)
    assert "error" in r
