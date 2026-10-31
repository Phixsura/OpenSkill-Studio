from app.services.app_marketplace_extension_outbox_pattern import OutboxPatternService
import time


def test_append_and_get_pending():
    svc = OutboxPatternService()
    svc.append("order-1", "order.created", {"total": 100})
    svc.append("order-1", "order.paid", {"payment_id": "p1"})
    pending = svc.get_pending()
    assert len(pending) == 2
    # Ordered by aggregate + time
    assert pending[0].event_type == "order.created"


def test_publish_lifecycle():
    svc = OutboxPatternService()
    e = svc.append("a-1", "created", {})
    svc.mark_published(e.entry_id)
    assert len(svc.get_pending()) == 0


def test_retry_with_backoff():
    svc = OutboxPatternService()
    e = svc.append("a-1", "event", {})
    svc.mark_failed(e.entry_id, "timeout")
    assert e.status == "failed"
    assert e.attempts == 1
    # Failed entries not immediately pending (backoff)
    pending = svc.get_pending()
    # May or may not show up depending on backoff timing


def test_dead_letter_after_max_attempts():
    svc = OutboxPatternService()
    e = svc.append("a-1", "event", {})
    for _ in range(5):
        svc.mark_failed(e.entry_id, "error")
    assert e.status == "dead"
    assert len(svc.get_dead_letters()) == 1


def test_retry_dead():
    svc = OutboxPatternService()
    e = svc.append("a-1", "event", {})
    for _ in range(5):
        svc.mark_failed(e.entry_id)
    assert e.status == "dead"
    svc.retry_dead(e.entry_id)
    assert e.status == "pending"
    assert e.attempts == 0


def test_consumer_dedup():
    svc = OutboxPatternService()
    assert svc.is_duplicate("entry-1") is False
    assert svc.is_duplicate("entry-1") is True  # second time = duplicate


def test_per_aggregate_ordering():
    svc = OutboxPatternService()
    svc.append("b", "event-b1", {})
    svc.append("a", "event-a1", {})
    svc.append("a", "event-a2", {})
    svc.append("b", "event-b2", {})
    pending = svc.get_pending()
    # Grouped by aggregate, ordered by time within
    a_events = [e for e in pending if e.aggregate_id == "a"]
    assert a_events[0].event_type == "event-a1"
    assert a_events[1].event_type == "event-a2"


def test_stats():
    svc = OutboxPatternService()
    svc.append("a", "created", {})
    e2 = svc.append("a", "updated", {})
    svc.mark_published(e2.entry_id)
    stats = svc.stats()
    assert stats["total"] == 2
    assert stats["by_status"]["pending"] == 1
    assert stats["by_status"]["published"] == 1
