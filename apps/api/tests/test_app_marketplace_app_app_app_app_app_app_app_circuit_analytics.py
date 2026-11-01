from app.services.app_marketplace_app_app_app_app_app_app_app_circuit_analytics import analyze_circuits, circuit_mttr

def test_analyze():
    r = analyze_circuits([
        {"service": "api", "event": "trip"},
        {"service": "api", "event": "recover", "open_duration_ms": 30000},
        {"service": "api", "event": "trip"},
        {"service": "db", "event": "trip"},
    ])
    assert r["total_trips"] == 3
    assert r["services"][0]["service"] == "api"
    assert r["services"][0]["trips"] == 2

def test_mttr():
    r = circuit_mttr([
        {"service": "api", "event": "trip", "timestamp": 1000},
        {"service": "api", "event": "recover", "timestamp": 1030},
        {"service": "api", "event": "trip", "timestamp": 2000},
        {"service": "api", "event": "recover", "timestamp": 2060},
    ])
    assert r["mttr_ms"] == 45  # avg(30, 60)
    assert r["recoveries"] == 2
