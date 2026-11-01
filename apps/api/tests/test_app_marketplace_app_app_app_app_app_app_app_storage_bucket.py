from app.services.app_marketplace_app_app_app_app_app_app_app_storage_bucket import (
    create_bucket, upload_object, bucket_stats, clear_buckets,
)

def test_create_upload():
    clear_buckets()
    r = create_bucket("my-assets", "eu-west-1")
    assert r["created"]
    upload_object("my-assets", "logo.png", 0.5)
    upload_object("my-assets", "bg.jpg", 2.3)
    s = bucket_stats()
    assert s["bucket_count"] == 1
    assert s["total_objects"] == 2
    assert s["total_size_mb"] == 2.8
    clear_buckets()

def test_duplicate():
    clear_buckets()
    create_bucket("test")
    r = create_bucket("test")
    assert not r["created"]
    clear_buckets()
