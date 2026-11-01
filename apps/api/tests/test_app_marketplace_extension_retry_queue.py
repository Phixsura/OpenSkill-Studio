from app.services.app_marketplace_extension_retry_queue import (
    RetryQueueService, RetryStrategy, ItemStatus,
)


def test_enqueue():
    svc = RetryQueueService()
    item = svc.enqueue("send_webhook", {"url": "https://a.com"})
    assert item.status == ItemStatus.PENDING
    assert item.attempt == 0


def test_failure_retries():
    svc = RetryQueueService()
    item = svc.enqueue("send", {}, max_attempts=3)
    svc.record_failure(item.item_id, "timeout")
    assert item.status == ItemStatus.RETRYING
    assert item.attempt == 1


def test_dead_letter_after_max():
    svc = RetryQueueService()
    item = svc.enqueue("send", {}, max_attempts=2)
    svc.record_failure(item.item_id, "err1")
    svc.record_failure(item.item_id, "err2")
    assert item.status == ItemStatus.DEAD_LETTER
    assert len(svc.get_dead_letters()) == 1


def test_success():
    svc = RetryQueueService()
    item = svc.enqueue("send", {})
    assert svc.record_success(item.item_id) is True
    assert item.status == ItemStatus.SUCCEEDED


def test_exponential_backoff():
    svc = RetryQueueService()
    item = svc.enqueue("op", {}, strategy=RetryStrategy.EXPONENTIAL, base_delay_ms=1000)
    svc.record_failure(item.item_id, "err")  # attempt 1: ~1000ms
    t1 = item.next_retry_at
    svc.record_failure(item.item_id, "err")  # attempt 2: ~2000ms
    t2 = item.next_retry_at
    assert t2 > t1  # second delay should be longer


def test_linear_backoff():
    svc = RetryQueueService()
    item = svc.enqueue("op", {}, strategy=RetryStrategy.LINEAR, base_delay_ms=500)
    svc.record_failure(item.item_id, "err")
    assert item.next_retry_at > 0


def test_retry_dead_letter():
    svc = RetryQueueService()
    item = svc.enqueue("send", {}, max_attempts=1)
    svc.record_failure(item.item_id, "err")
    assert item.status == ItemStatus.DEAD_LETTER
    assert svc.retry_dead_letter(item.item_id, extra_attempts=2) is True
    assert item.status == ItemStatus.RETRYING
    assert item.max_attempts == 3


def test_stats():
    svc = RetryQueueService()
    svc.enqueue("a", {})
    item = svc.enqueue("b", {}, max_attempts=1)
    svc.record_failure(item.item_id, "err")
    stats = svc.get_stats()
    assert stats["pending"] == 1
    assert stats["dead_letter"] == 1
