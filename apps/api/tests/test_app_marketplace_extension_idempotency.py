from app.services.app_marketplace_extension_idempotency import IdempotencyService


def test_first_request():
    svc = IdempotencyService()
    is_dup, cached, _ = svc.check("key-1")
    assert is_dup is False
    assert cached is None


def test_duplicate_detection():
    svc = IdempotencyService()
    svc.record("key-2", {"id": "order-1"}, 201)
    is_dup, cached, code = svc.check("key-2")
    assert is_dup is True
    assert cached == {"id": "order-1"}
    assert code == 201


def test_expired_key():
    svc = IdempotencyService()
    svc.record("key-3", {"ok": True}, 200, ttl=-1.0)
    is_dup, _, _ = svc.check("key-3")
    assert is_dup is False


def test_execute_once():
    svc = IdempotencyService()
    call_count = [0]
    def create_order():
        call_count[0] += 1
        return {"order_id": "o1"}, 201

    r1, s1, cached1 = svc.execute_once("create-1", create_order)
    r2, s2, cached2 = svc.execute_once("create-1", create_order)
    assert call_count[0] == 1  # only called once
    assert cached1 is False
    assert cached2 is True
    assert r1 == r2


def test_invalidate():
    svc = IdempotencyService()
    svc.record("key-4", {}, 200)
    assert svc.invalidate("key-4") is True
    is_dup, _, _ = svc.check("key-4")
    assert is_dup is False


def test_cleanup():
    svc = IdempotencyService()
    svc.record("fresh", {}, 200, ttl=3600)
    svc.record("stale", {}, 200, ttl=-1)
    cleaned = svc.cleanup_expired()
    assert cleaned == 1
    assert svc.stats()["active"] == 1
