from app.services.app_marketplace_app_app_app_app_app_app_app_traffic_analyze import analyze_traffic, detect_traffic_spike

def test_analyze():
    r = analyze_traffic([
        {"endpoint": "/users", "method": "GET", "status": 200, "latency_ms": 50},
        {"endpoint": "/users", "method": "GET", "status": 200, "latency_ms": 60},
        {"endpoint": "/orders", "method": "POST", "status": 500, "latency_ms": 200},
    ])
    assert r["total"] == 3
    assert r["error_rate_pct"] == 33.33
    assert r["top_endpoints"][0]["endpoint"] == "/users"

def test_spike():
    r = detect_traffic_spike(300, 100, threshold_multiplier=2.0)
    assert r["spike_detected"]
    assert r["ratio"] == 3.0

def test_no_spike():
    r = detect_traffic_spike(120, 100)
    assert not r["spike_detected"]
