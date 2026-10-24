from app.services.app_marketplace_app_app_app_app_app_app_app_latency_track import bucket_latencies

def test_bucket():
    r = bucket_latencies([5, 8, 25, 75, 150, 600])
    assert r["buckets"]["<10ms"] == 2
    assert r["buckets"]["10-50ms"] == 1
    assert r["buckets"][">500ms"] == 1
    assert r["total"] == 6
