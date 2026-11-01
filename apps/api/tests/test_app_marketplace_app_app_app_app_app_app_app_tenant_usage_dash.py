from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_usage_dash import tenant_dashboard

def test_ok():
    r = tenant_dashboard({"id": "t1", "plan": "pro", "api_calls": 5000, "api_limit": 100000,
                           "storage_gb": 20, "storage_limit_gb": 100,
                           "bandwidth_gb": 100, "bandwidth_limit_gb": 500})
    assert r["status"] == "ok"

def test_warning():
    r = tenant_dashboard({"id": "t2", "api_calls": 85000, "api_limit": 100000,
                           "storage_gb": 10, "storage_limit_gb": 100,
                           "bandwidth_gb": 50, "bandwidth_limit_gb": 500})
    assert r["status"] == "warning"

def test_exceeded():
    r = tenant_dashboard({"id": "t3", "api_calls": 120000, "api_limit": 100000,
                           "storage_gb": 10, "storage_limit_gb": 100,
                           "bandwidth_gb": 50, "bandwidth_limit_gb": 500})
    assert r["status"] == "exceeded"
