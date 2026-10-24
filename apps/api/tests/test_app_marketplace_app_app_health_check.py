from app.services.app_marketplace_app_app_health_check import probe_endpoint, build_health_dashboard

def test_probe_ok():
    r = probe_endpoint(url="https://api.example.com/health")
    assert r["healthy"]
    assert r["within_timeout"]

def test_probe_bad_scheme():
    r = probe_endpoint(url="ftp://bad.com")
    assert not r["healthy"]

def test_dashboard():
    eps = [
        {"name": "API", "url": "https://api.example.com/health"},
        {"name": "Web", "url": "https://web.example.com"},
    ]
    r = build_health_dashboard(endpoints=eps)
    assert r["total"] == 2
    assert r["overall"] == "healthy"
