from app.services.app_marketplace_app_content_delivery import configure_cdn, purge_cache, get_cdn_stats

def test_configure():
    r = configure_cdn(app_id="a1", regions=["us-east", "eu-west"], cache_ttl_sec=7200)
    assert len(r["regions"]) == 2
    assert r["cache_ttl_sec"] == 7200
    assert r["status"] == "active"

def test_no_valid():
    r = configure_cdn(app_id="a1", regions=["mars"])
    assert "error" in r

def test_purge():
    r = purge_cache(app_id="a1", paths=["/assets/*"])
    assert r["purge_type"] == "selective"

def test_full_purge():
    r = purge_cache(app_id="a1")
    assert r["purge_type"] == "full"

def test_stats():
    r = get_cdn_stats(app_id="a1")
    assert r["cache_hit_rate"] == 94.5
