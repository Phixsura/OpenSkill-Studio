from app.services.app_marketplace_app_app_app_app_app_app_app_idem_handler import IdempotentHandler

def test_idempotent():
    ih = IdempotentHandler()
    call_count = 0
    def handler():
        nonlocal call_count
        call_count += 1
        return {"order_id": "o1"}
    r1 = ih.handle("key-1", handler)
    assert not r1["cached"]
    r2 = ih.handle("key-1", handler)
    assert r2["cached"]
    assert r2["result"]["order_id"] == "o1"
    assert call_count == 1  # handler only called once

def test_cleanup():
    ih = IdempotentHandler(ttl_seconds=10)
    ih.handle("k1", lambda: {"ok": True})
    import time
    r = ih.cleanup(now=time.time() + 11)
    assert r["removed"] == 1
