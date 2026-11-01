from app.services.app_marketplace_app_app_app_app_app_app_app_usage_analytics import aggregate_usage, top_consumers

def test_aggregate():
    r = aggregate_usage([
        {"endpoint": "/users", "latency_ms": 50, "status": 200},
        {"endpoint": "/users", "latency_ms": 60, "status": 200},
        {"endpoint": "/orders", "latency_ms": 100, "status": 500},
    ])
    assert r["total_requests"] == 3
    assert r["unique_endpoints"] == 2
    assert r["endpoints"][0]["endpoint"] == "/users"
    assert r["endpoints"][1]["error_rate"] == 100.0

def test_top_consumers():
    r = top_consumers([
        {"user_id": "u1"}, {"user_id": "u1"}, {"user_id": "u1"},
        {"user_id": "u2"}, {"user_id": "u2"},
    ], limit=2)
    assert r[0]["user_id"] == "u1"
    assert r[0]["count"] == 3
    assert len(r) == 2
