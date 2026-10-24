from app.services.app_marketplace_app_app_app_app_app_app_app_rate_analyze import analyze_rate

def test_normal():
    # 100 requests over 100 seconds
    ts = [float(i) for i in range(100)]
    r = analyze_rate(ts, window_seconds=10)
    assert r["rps"] > 0
    assert not r["spike_detected"]

def test_spike():
    # Normal traffic then burst
    ts = [float(i) for i in range(10)]  # 1 per second
    ts += [10.0 + i * 0.01 for i in range(100)]  # 100 in 1 second
    r = analyze_rate(ts, window_seconds=5)
    assert r["spike_detected"]
