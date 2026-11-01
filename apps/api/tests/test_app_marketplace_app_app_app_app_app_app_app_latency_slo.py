from app.services.app_marketplace_app_app_app_app_app_app_app_latency_slo import check_latency_slo

def test_slo():
    r = check_latency_slo([
        {"endpoint": "/api/users", "p99_ms": 100, "target_p99_ms": 200},
        {"endpoint": "/api/reports", "p99_ms": 800, "target_p99_ms": 500},
        {"endpoint": "/api/health", "p99_ms": 5, "target_p99_ms": 50},
    ])
    assert r["met"] == 2
    assert r["breached"] == 1
    assert r["compliance_pct"] == 66.7
    assert r["endpoints"][0]["headroom_ms"] == 100
