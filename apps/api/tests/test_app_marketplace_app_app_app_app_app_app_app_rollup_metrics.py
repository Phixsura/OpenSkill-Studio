from app.services.app_marketplace_app_app_app_app_app_app_app_rollup_metrics import rollup, compute_rate

def test_rollup():
    points = [{"timestamp": i * 30, "value": i * 10} for i in range(20)]  # 0-570s
    r = rollup(points, bucket_minutes=5)
    assert r["total_points"] == 20
    assert r["bucket_count"] >= 1
    assert r["buckets"][0]["count"] >= 1
    assert "avg" in r["buckets"][0]

def test_rate():
    points = [{"timestamp": i * 10} for i in range(10)]  # 0-90s, 10 points
    r = compute_rate(points, window_sec=60)
    assert r["rate"] > 0
    assert r["duration"] == 90
