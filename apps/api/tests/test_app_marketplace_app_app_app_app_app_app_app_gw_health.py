from app.services.app_marketplace_app_app_app_app_app_app_app_gw_health import gateway_health

def test_health():
    r = gateway_health([
        {"name": "gw-1", "region": "us-east", "status": "healthy", "latency_ms": 10},
        {"name": "gw-2", "region": "us-east", "status": "healthy", "latency_ms": 12},
        {"name": "gw-3", "region": "eu-west", "status": "degraded", "latency_ms": 50},
    ])
    assert r["healthy"] == 2
    assert not r["all_healthy"]
    assert r["by_region"]["us-east"]["healthy"] == 2
    assert r["avg_latency_ms"] == 24.0
