from app.services.app_marketplace_app_app_app_app_app_app_app_idempotency import IdempotencyManager

def test_first_request():
    im = IdempotencyManager()
    r = im.check_or_create("req-1")
    assert not r["duplicate"]
    im.store_response("req-1", {"order_id": "o1"})

def test_duplicate():
    im = IdempotencyManager()
    im.check_or_create("req-1")
    im.store_response("req-1", {"order_id": "o1"})
    r = im.check_or_create("req-1")
    assert r["duplicate"]
    assert r["original_response"]["order_id"] == "o1"

def test_expiry():
    im = IdempotencyManager(ttl_seconds=10)
    im.check_or_create("req-1", now=100)
    im.store_response("req-1", {"ok": True})
    r = im.check_or_create("req-1", now=111)
    assert not r["duplicate"]  # expired
