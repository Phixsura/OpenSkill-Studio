from app.services.app_marketplace_app_app_app_app_app_app_app_size_limiter import check_request_size, batch_check

def test_allowed():
    r = check_request_size(512000, max_bytes=1048576)
    assert r["allowed"]
    assert r["human_size"] == "500.0KB"

def test_rejected():
    r = check_request_size(2000000, max_bytes=1048576)
    assert not r["allowed"]

def test_batch():
    r = batch_check([
        {"path": "/upload", "size_bytes": 500000},
        {"path": "/big", "size_bytes": 2000000},
    ], max_bytes=1048576)
    assert r["rejected"] == 1
    assert r["accepted"] == 1
