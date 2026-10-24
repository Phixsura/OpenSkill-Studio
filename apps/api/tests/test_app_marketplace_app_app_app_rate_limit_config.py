from app.services.app_marketplace_app_app_app_rate_limit_config import build_rate_limit_config, validate_rate_limit

def test_config():
    endpoints = [
        {"method": "GET", "path": "/api/apps"},
        {"method": "POST", "path": "/api/apps", "rpm": 60, "burst": 10},
    ]
    r = build_rate_limit_config(endpoints=endpoints)
    assert r["total"] == 2
    assert r["custom_count"] == 1
    assert r["endpoints"][0]["rpm"] == 600  # default

def test_validate_ok():
    r = validate_rate_limit(rpm=100, burst=20)
    assert r["valid"]

def test_validate_burst_exceeds():
    r = validate_rate_limit(rpm=10, burst=50)
    assert not r["valid"]
    assert "Burst" in r["errors"][0]
