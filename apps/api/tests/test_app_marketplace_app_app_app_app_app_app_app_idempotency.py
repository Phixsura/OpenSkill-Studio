from app.services.app_marketplace_app_app_app_app_app_app_app_idempotency import (
    check_or_store, store_response, key_stats, clear_keys,
)

def test_idempotency():
    clear_keys()
    r1 = check_or_store("pay_123")
    assert not r1["is_duplicate"]
    store_response("pay_123", {"status": "ok", "amount": 100})
    r2 = check_or_store("pay_123")
    assert r2["is_duplicate"]
    assert r2["original_response"]["amount"] == 100
    clear_keys()

def test_stats():
    clear_keys()
    check_or_store("a")
    check_or_store("b")
    store_response("a", {"ok": True})
    s = key_stats()
    assert s["total"] == 2
    assert s["with_response"] == 1
    clear_keys()
