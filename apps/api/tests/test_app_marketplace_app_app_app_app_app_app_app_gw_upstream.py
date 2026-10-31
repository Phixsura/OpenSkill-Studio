from app.services.app_marketplace_app_app_app_app_app_app_app_gw_upstream import check_upstreams

def test_healthy():
    r = check_upstreams([
        {"name": "api-1", "address": "10.0.0.1:8080", "successes": 990, "total": 1000, "total_ms": 50000},
        {"name": "api-2", "address": "10.0.0.2:8080", "successes": 995, "total": 1000, "total_ms": 45000},
    ])
    assert r["all_healthy"]
    assert r["healthy"] == 2

def test_unhealthy():
    r = check_upstreams([
        {"name": "api-1", "successes": 500, "total": 1000, "total_ms": 50000},
    ])
    assert not r["all_healthy"]
    assert r["unhealthy"] == 1
