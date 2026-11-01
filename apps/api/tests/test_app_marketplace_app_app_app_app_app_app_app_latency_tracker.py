from app.services.app_marketplace_app_app_app_app_app_app_app_latency_tracker import compute_percentiles, compare_latency

def test_percentiles():
    samples = list(range(1, 101))  # 1..100
    r = compute_percentiles(samples)
    assert r["count"] == 100
    assert r["p50"] == 50.5
    assert r["p99"] == 99.01
    assert r["min"] == 1
    assert r["max"] == 100
    assert r["status"] == "fast"

def test_compare():
    cur = compute_percentiles([100, 150, 200, 250, 300])
    prev = compute_percentiles([80, 120, 160, 200, 240])
    c = compare_latency(cur, prev)
    assert c["comparable"]
    assert c["changes"]["p50"]["direction"] == "slower"
