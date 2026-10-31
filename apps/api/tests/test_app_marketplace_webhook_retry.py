from app.services.app_marketplace_webhook_retry import (
    WebhookRetryManager, DeliveryStatus,
)


def test_create_and_succeed():
    rm = WebhookRetryManager()
    rm.create_delivery("d1", "sub-1", "https://hook.test", "event.fired", {"data": 1})
    assert rm.record_success("d1") is True
    assert rm.get_delivery("d1").status == DeliveryStatus.DELIVERED


def test_retry_on_failure():
    rm = WebhookRetryManager()
    rm.create_delivery("d2", "sub-1", "https://hook.test", "e", {}, max_attempts=3)
    status = rm.record_failure("d2", "Connection refused")
    assert status == DeliveryStatus.RETRYING
    assert rm.get_delivery("d2").attempt == 1
    assert len(rm.get_retryable()) == 1


def test_dead_letter_after_max_attempts():
    rm = WebhookRetryManager()
    rm.create_delivery("d3", "sub-1", "https://hook.test", "e", {}, max_attempts=2)
    rm.record_failure("d3", "Error 1")
    status = rm.record_failure("d3", "Error 2")
    assert status == DeliveryStatus.DEAD_LETTER
    assert len(rm.get_dead_letter_queue()) == 1


def test_exponential_backoff():
    rm = WebhookRetryManager(base_delay_seconds=10.0, max_delay_seconds=1000.0)
    assert rm.calculate_backoff(0) == 10.0
    assert rm.calculate_backoff(1) == 20.0
    assert rm.calculate_backoff(2) == 40.0
    assert rm.calculate_backoff(10) == 1000.0  # capped


def test_stats():
    rm = WebhookRetryManager()
    rm.create_delivery("s1", "sub", "url", "e", {})
    rm.create_delivery("s2", "sub", "url", "e", {})
    rm.create_delivery("s3", "sub", "url", "e", {}, max_attempts=1)
    rm.record_success("s1")
    rm.record_failure("s2", "err")
    rm.record_failure("s3", "err")  # goes to dead letter
    stats = rm.get_stats()
    assert stats["delivered"] == 1
    assert stats["retrying"] == 1
    assert stats["dead_letter"] == 1
