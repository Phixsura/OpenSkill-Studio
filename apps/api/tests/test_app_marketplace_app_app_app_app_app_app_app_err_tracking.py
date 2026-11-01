from app.services.app_marketplace_app_app_app_app_app_app_app_err_tracking import track_errors, error_trend

def test_track():
    r = track_errors([
        {"type": "TypeError", "service": "api", "timestamp": 100},
        {"type": "TypeError", "service": "api", "timestamp": 200},
        {"type": "TypeError", "service": "worker", "timestamp": 300},
        {"type": "ConnectionError", "service": "api", "timestamp": 150},
    ])
    assert r["total_errors"] == 4
    assert r["unique_types"] == 2
    assert r["top_error"] == "TypeError"
    assert r["errors"][0]["service_count"] == 2

def test_trend():
    r = error_trend(50, 100)
    assert r["trend"] == "decreasing"
    assert r["pct_change"] == -50.0
