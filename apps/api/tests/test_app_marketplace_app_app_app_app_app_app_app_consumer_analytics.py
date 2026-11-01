from app.services.app_marketplace_app_app_app_app_app_app_app_consumer_analytics import analyze_consumers

def test_analytics():
    r = analyze_consumers([
        {"consumer_id": "app-1", "status": 200, "latency_ms": 50},
        {"consumer_id": "app-1", "status": 200, "latency_ms": 60},
        {"consumer_id": "app-2", "status": 500, "latency_ms": 200},
        {"consumer_id": "app-2", "status": 200, "latency_ms": 40},
    ])
    assert r["total_consumers"] == 2
    assert r["consumers"][0]["consumer_id"] == "app-1"
    assert r["consumers"][0]["requests"] == 2
    assert r["consumers"][1]["error_rate_pct"] == 50.0
