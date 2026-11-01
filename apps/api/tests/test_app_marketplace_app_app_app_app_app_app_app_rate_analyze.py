from app.services.app_marketplace_app_app_app_app_app_app_app_rate_analyze import analyze_rate

def test_normal():
    ts = [float(i) for i in range(100)]
    r = analyze_rate(ts, window_seconds=10)
    assert r["rps"] > 0
    assert not r["spike_detected"]

def test_spike():
    # 5 windows of ~2 requests each, then one window with 50
    ts = [float(i * 5) for i in range(10)]  # spread over 50s
    ts += [100.0 + i * 0.01 for i in range(50)]  # 50 in <1s at t=100
    r = analyze_rate(ts, window_seconds=10)
    assert r["spike_detected"]
