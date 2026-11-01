from app.services.app_marketplace_extension_idempotency_store import IdempotencyStoreService
import time


def test_new_request():
    store = IdempotencyStoreService()
    status, _ = store.check("req-1")
    assert status == "new"


def test_complete_and_replay():
    store = IdempotencyStoreService()
    store.start("req-1", "POST", "/orders", '{"item":"widget"}')
    store.complete("req-1", {"order_id": "o1"}, 201)
    status, cached = store.check("req-1", "POST", "/orders", '{"item":"widget"}')
    assert status == "completed"
    assert cached["response"]["order_id"] == "o1"
    assert cached["replayed"] is True


def test_in_progress_blocks():
    store = IdempotencyStoreService()
    store.start("req-1")
    status, _ = store.check("req-1")
    assert status == "in_progress"


def test_fail_allows_retry():
    store = IdempotencyStoreService()
    store.start("req-1")
    store.fail("req-1")
    status, _ = store.check("req-1")
    assert status == "new"  # can retry


def test_fingerprint_conflict():
    store = IdempotencyStoreService()
    store.start("req-1", "POST", "/orders", '{"item":"a"}')
    store.complete("req-1", {"ok": True})
    # Same key but different body = conflict
    status, _ = store.check("req-1", "POST", "/orders", '{"item":"b"}')
    assert status == "conflict"


def test_expiry():
    store = IdempotencyStoreService()
    store.start("req-1", ttl=0)  # immediate TTL via default
    entry = store._entries["req-1"]
    entry.expires_at = time.time() - 1  # force expired
    store.complete("req-1", {})
    status, _ = store.check("req-1")
    assert status == "new"  # expired → treated as new


def test_replay_count():
    store = IdempotencyStoreService()
    store.start("req-1")
    store.complete("req-1", {"ok": True})
    store.check("req-1")
    store.check("req-1")
    _, cached = store.check("req-1")
    assert cached["replay_count"] == 3


def test_stats():
    store = IdempotencyStoreService()
    store.start("a"); store.complete("a", {})
    store.start("b"); store.complete("b", {})
    store.start("c")  # in progress
    store.check("a")  # replay
    stats = store.stats()
    assert stats["completed"] == 2
    assert stats["in_progress"] == 1
    assert stats["total_replays"] == 1
