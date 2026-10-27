from app.services.app_marketplace_extension_request_dedup import RequestDedupService
import time


def test_explicit_idempotency_key():
    svc = RequestDedupService()
    is_dup, _ = svc.check(idempotency_key="req-123")
    assert is_dup is False  # first time
    key = svc.start(idempotency_key="req-123")
    svc.complete(key, {"id": "order-1"}, 201)
    is_dup, resp = svc.check(idempotency_key="req-123")
    assert is_dup is True
    assert resp["id"] == "order-1"


def test_content_hash_dedup():
    svc = RequestDedupService()
    # Same method+path+body = same hash
    key = svc.start(method="POST", path="/api/orders", body='{"item":"widget"}')
    svc.complete(key, {"created": True})
    is_dup, resp = svc.check(method="POST", path="/api/orders", body='{"item":"widget"}')
    assert is_dup is True
    assert resp["created"] is True


def test_different_body_not_dedup():
    svc = RequestDedupService()
    key = svc.start(method="POST", path="/api/orders", body='{"item":"a"}')
    svc.complete(key, {"item": "a"})
    is_dup, _ = svc.check(method="POST", path="/api/orders", body='{"item":"b"}')
    assert is_dup is False


def test_inflight_detection():
    svc = RequestDedupService()
    svc.start(idempotency_key="req-456")
    is_dup, resp = svc.check(idempotency_key="req-456")
    assert is_dup is True
    assert resp is None  # no response yet


def test_expired_entry():
    svc = RequestDedupService()
    key = svc.start(idempotency_key="req-expire")
    svc.complete(key, {"ok": True}, ttl=0)  # TTL=0 means DEFAULT_TTL
    # Manually expire
    svc._cache[key].expires_at = time.time() - 1
    is_dup, resp = svc.check(idempotency_key="req-expire")
    assert is_dup is False


def test_cancel_clears_inflight():
    svc = RequestDedupService()
    svc.start(idempotency_key="req-fail")
    svc.cancel("req-fail")
    is_dup, _ = svc.check(idempotency_key="req-fail")
    assert is_dup is False


def test_hit_count_tracking():
    svc = RequestDedupService()
    key = svc.start(idempotency_key="req-hits")
    svc.complete(key, {"ok": True})
    svc.check(idempotency_key="req-hits")
    svc.check(idempotency_key="req-hits")
    svc.check(idempotency_key="req-hits")
    assert svc._cache["req-hits"].hit_count == 3


def test_stats():
    svc = RequestDedupService()
    key1 = svc.start(idempotency_key="a")
    svc.complete(key1, {"ok": True})
    svc.start(idempotency_key="b")  # inflight
    svc.check(idempotency_key="a")
    stats = svc.get_stats()
    assert stats["cached_responses"] == 1
    assert stats["inflight"] == 1
    assert stats["total_dedup_hits"] == 1
