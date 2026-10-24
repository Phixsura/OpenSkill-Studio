from app.services.app_marketplace_app_api_latency_histogram import build_histogram

def test_histogram():
    latencies = [5, 10, 15, 50, 100, 200, 500, 1000, 3000]
    r = build_histogram(latencies_ms=latencies)
    assert r["total"] == 9
    assert r["min_ms"] == 5
    assert r["max_ms"] == 3000
    assert r["p50_ms"] == 100
    assert len(r["histogram"]) == 12  # 11 buckets + inf

def test_empty():
    r = build_histogram(latencies_ms=[])
    assert r["total"] == 0
    assert r["avg_ms"] == 0

def test_custom_buckets():
    r = build_histogram(latencies_ms=[10, 20, 30], buckets=[15, 25, 50])
    assert len(r["histogram"]) == 4  # 3 + inf
    assert r["histogram"][0]["count"] == 1  # 10 <= 15
