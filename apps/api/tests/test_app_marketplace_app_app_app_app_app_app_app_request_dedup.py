from app.services.app_marketplace_app_app_app_app_app_app_app_request_dedup import RequestDeduplicator

def test_dedup():
    d = RequestDeduplicator(ttl_sec=60)
    r1 = d.check("key-1", now=100)
    assert not r1["duplicate"]
    d.record("key-1", {"status": "created", "id": "abc"}, now=100)
    r2 = d.check("key-1", now=110)
    assert r2["duplicate"]
    assert r2["original_response"]["id"] == "abc"
    # After TTL
    r3 = d.check("key-1", now=200)
    assert not r3["duplicate"]
    assert d.stats()["tracked_keys"] == 0
