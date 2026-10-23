from app.services.app_marketplace_app_app_app_app_app_app_app_token_bucket import (
    create_bucket, consume, bucket_status, clear_buckets,
)

def test_consume():
    clear_buckets()
    create_bucket("api", capacity=10, refill_rate=1.0)
    for _ in range(10):
        r = consume("api")
        assert r["allowed"]
    r = consume("api")
    assert not r["allowed"]
    assert r["retry_after_sec"] > 0
    clear_buckets()

def test_status():
    clear_buckets()
    create_bucket("test", capacity=100, refill_rate=10)
    consume("test", 30)
    s = bucket_status("test")
    assert s["tokens"] == 70
    assert s["fill_pct"] == 70
    clear_buckets()
