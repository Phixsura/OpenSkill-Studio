from app.services.app_marketplace_app_app_endpoint_tester import test_endpoint as check_endpoint, run_test_suite

def test_valid_endpoint():
    r = check_endpoint(url="https://api.example.com/health")
    assert r["pass"]
    assert r["actual_status"] == 200

def test_bad_ep_scheme():
    r = check_endpoint(url="ftp://bad.com")
    assert not r["pass"]

def test_suite():
    endpoints = [
        {"url": "https://api.example.com/v1/apps"},
        {"url": "https://api.example.com/v1/users", "method": "GET"},
    ]
    r = run_test_suite(endpoints=endpoints)
    assert r["all_pass"]
    assert r["total"] == 2
    assert r["avg_response_ms"] == 45
