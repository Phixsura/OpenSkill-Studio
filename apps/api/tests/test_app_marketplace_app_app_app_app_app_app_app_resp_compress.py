from app.services.app_marketplace_app_app_app_app_app_app_app_resp_compress import should_compress, compress_stats

def test_should():
    r = should_compress(5000, "application/json", "gzip, deflate")
    assert r["should_compress"]
    assert r["encoding"] == "gzip"

def test_too_small():
    r = should_compress(500, "application/json", "gzip")
    assert not r["should_compress"]

def test_no_gzip():
    r = should_compress(5000, "application/json", "deflate")
    assert not r["should_compress"]

def test_stats():
    r = compress_stats(10000, 8000, 52428800)
    assert r["compression_rate"] == 80.0
    assert r["saved_mb"] == 50.0
