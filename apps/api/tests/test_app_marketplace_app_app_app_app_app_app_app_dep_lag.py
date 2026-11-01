from app.services.app_marketplace_app_app_app_app_app_app_app_dep_lag import detect_lag

def test_detect():
    r = detect_lag([
        {"source": "api", "destination": "db", "latency_ms": 300},
        {"source": "api", "destination": "db", "latency_ms": 400},
        {"source": "api", "destination": "cache", "latency_ms": 5},
        {"source": "api", "destination": "cache", "latency_ms": 3},
    ], threshold_ms=100)
    assert r["lagging_count"] == 1
    assert r["lagging_pairs"][0]["destination"] == "db"
    assert r["total_pairs"] == 2
