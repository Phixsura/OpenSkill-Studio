from app.services.app_marketplace_app_app_app_app_app_app_app_response_time import track_response_times

def test_response():
    samples = [50, 80, 60, 100, 45, 90, 150, 200, 300, 55]
    r = track_response_times(samples, sla_ms=200)
    assert r["count"] == 10
    assert r["avg"] > 0
    assert r["p50"] > 0
    assert r["p95"] > 0
    assert r["sla_pct"] > 0
    assert r["status"] in ("fast", "ok", "slow")

def test_empty():
    r = track_response_times([])
    assert "error" in r
