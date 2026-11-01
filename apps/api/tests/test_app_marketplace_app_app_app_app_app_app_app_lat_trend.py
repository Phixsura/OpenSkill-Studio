from app.services.app_marketplace_app_app_app_app_app_app_app_lat_trend import latency_trend

def test_worsening():
    r = latency_trend([{"p99_ms": 50}, {"p99_ms": 60}, {"p99_ms": 100}, {"p99_ms": 120}])
    assert r["trend"] == "worsening"

def test_improving():
    r = latency_trend([{"p99_ms": 200}, {"p99_ms": 180}, {"p99_ms": 80}, {"p99_ms": 60}])
    assert r["trend"] == "improving"
