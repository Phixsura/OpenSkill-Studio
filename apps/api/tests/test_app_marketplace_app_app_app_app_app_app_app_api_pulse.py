from app.services.app_marketplace_app_app_app_app_app_app_app_api_pulse import pulse_check, pulse_trend

def test_pulse():
    r = pulse_check([
        {"status": "healthy", "latency_ms": 50, "rps": 500, "errors": 0},
        {"status": "healthy", "latency_ms": 80, "rps": 200, "errors": 1},
    ])
    assert r["pulse"] == "strong"
    assert r["healthy"] == 2
    assert r["total_rps"] == 700

def test_trend():
    r = pulse_trend([{"healthy": 5}, {"healthy": 7}])
    assert r["improving"]
