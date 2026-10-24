from app.services.app_marketplace_app_app_app_app_app_app_app_req_dedup import RequestDeduplicator

def test_dedup():
    d = RequestDeduplicator(ttl_seconds=60)
    r1 = d.check("POST", "/api/orders", "abc123")
    assert not r1["is_duplicate"]
    r2 = d.check("POST", "/api/orders", "abc123")
    assert r2["is_duplicate"]
    r3 = d.check("POST", "/api/orders", "def456")
    assert not r3["is_duplicate"]
    assert d.stats()["cached_keys"] == 2
