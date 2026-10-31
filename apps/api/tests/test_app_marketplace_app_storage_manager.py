from app.services.app_marketplace_app_storage_manager import create_bucket, get_storage_usage

def test_create():
    r = create_bucket(app_id="a1", name="uploads", access="public-read")
    assert r["bucket_id"].startswith("bkt_")
    assert r["access"] == "public-read"

def test_invalid_access():
    r = create_bucket(app_id="a1", name="x", access="world-writable")
    assert "error" in r

def test_usage():
    buckets = [{"name": "uploads", "size_bytes": 1073741824, "object_count": 500},
               {"name": "backups", "size_bytes": 536870912, "object_count": 50}]
    r = get_storage_usage(buckets=buckets)
    assert r["total_size_gb"] == 1.5
    assert r["total_objects"] == 550
