from app.services.app_marketplace_app_app_app_app_app_app_app_cdn_cache import CdnCacheManager

def test_cdn():
    mgr = CdnCacheManager()
    mgr.add_zone("z1", domain="cdn.example.com")
    for _ in range(8):
        mgr.record_request("z1", "/js/app.js", cache_hit=True)
    for _ in range(2):
        mgr.record_request("z1", "/api/data", cache_hit=False)
    s = mgr.stats("z1")
    assert s["hit_rate"] == 80.0
    assert s["health"] == "good"
    mgr.purge("z1", paths=["/js/app.js"])
    s2 = mgr.stats("z1")
    assert s2["purges"] == 1
