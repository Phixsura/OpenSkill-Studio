from app.services.app_marketplace_app_app_app_app_app_app_app_dns_monitor import monitor_dns

def test_monitor():
    r = monitor_dns([
        {"domain": "api.example.com", "resolve_ms": 5, "resolved": True, "threshold_ms": 50},
        {"domain": "slow.example.com", "resolve_ms": 200, "resolved": True, "threshold_ms": 50},
        {"domain": "down.example.com", "resolve_ms": 0, "resolved": False},
    ])
    assert r["healthy"] == 1
    assert r["unhealthy"] == 2
    assert not r["all_healthy"]
