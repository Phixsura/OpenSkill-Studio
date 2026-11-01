"""Tests for Webhook Retry Queue — backoff, dead-letter, circuit breaker."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.webhook_retry_queue import (
    CIRCUIT_BREAKER_THRESHOLD,
    DeliveryStatus,
    EndpointCircuitBreaker,
    WebhookRetryQueue,
    WebhookTask,
    compute_backoff,
    compute_signature,
)


class TestComputeBackoff:
    def test_first_attempt_near_base(self):
        delays = [compute_backoff(1, jitter=0) for _ in range(10)]
        assert all(d == pytest.approx(10.0) for d in delays)

    def test_exponential_growth(self):
        d1 = compute_backoff(1, jitter=0)
        d2 = compute_backoff(2, jitter=0)
        d3 = compute_backoff(3, jitter=0)
        assert d2 == pytest.approx(30.0)
        assert d3 == pytest.approx(90.0)

    def test_jitter_adds_variance(self):
        delays = {round(compute_backoff(3, jitter=0.2), 1) for _ in range(50)}
        # With jitter, we should get more than one distinct value
        assert len(delays) > 1

    def test_never_negative(self):
        for attempt in range(1, 10):
            assert compute_backoff(attempt) > 0

    def test_fifth_attempt_near_810(self):
        d = compute_backoff(5, jitter=0)
        assert d == pytest.approx(810.0)


class TestComputeSignature:
    def test_produces_sha256_prefixed_hex(self):
        sig = compute_signature(b'{"event":"test"}', "secret123")
        assert sig.startswith("sha256=")
        assert len(sig) == 7 + 64  # "sha256=" + 64 hex chars

    def test_deterministic(self):
        payload = b'{"id":"abc"}'
        s1 = compute_signature(payload, "key")
        s2 = compute_signature(payload, "key")
        assert s1 == s2

    def test_different_secrets_differ(self):
        payload = b'{"id":"abc"}'
        s1 = compute_signature(payload, "key1")
        s2 = compute_signature(payload, "key2")
        assert s1 != s2


class TestEndpointCircuitBreaker:
    def test_starts_closed(self):
        cb = EndpointCircuitBreaker(endpoint_url="https://example.com/hook")
        assert cb.is_open is False
        assert cb.should_allow() is True

    def test_opens_after_threshold_failures(self):
        cb = EndpointCircuitBreaker(endpoint_url="https://example.com/hook")
        for _ in range(CIRCUIT_BREAKER_THRESHOLD):
            cb.record_failure()
        assert cb.is_open is True
        assert cb.should_allow() is False

    def test_success_resets(self):
        cb = EndpointCircuitBreaker(endpoint_url="https://example.com/hook")
        for _ in range(5):
            cb.record_failure()
        cb.record_success()
        assert cb.consecutive_failures == 0
        assert cb.is_open is False

    def test_half_open_after_cooldown(self):
        cb = EndpointCircuitBreaker(endpoint_url="https://example.com/hook")
        for _ in range(CIRCUIT_BREAKER_THRESHOLD):
            cb.record_failure()
        assert cb.should_allow() is False

        # Simulate cooldown passed
        cb.opened_at = datetime.now(UTC) - timedelta(seconds=600)
        assert cb.should_allow() is True


class TestWebhookRetryQueue:
    def _make_task(self, task_id: str = "task-1", url: str = "https://app.example.com/webhook") -> WebhookTask:
        return WebhookTask(
            task_id=task_id,
            webhook_url=url,
            payload={"event": "test", "data": {"id": "123"}},
            event_type="test.created",
            secret="webhook-secret",
        )

    def test_enqueue_and_get_pending(self):
        q = WebhookRetryQueue()
        task = self._make_task()
        q.enqueue(task)
        assert q.queue_size() == 1
        pending = q.get_pending()
        assert len(pending) == 1
        assert pending[0].task_id == "task-1"

    def test_successful_delivery(self):
        q = WebhookRetryQueue()
        q.enqueue(self._make_task())
        result = q.record_attempt("task-1", status_code=200, latency_ms=45.0)
        assert result.status == DeliveryStatus.DELIVERED
        assert result.attempt_count == 1
        assert q.queue_size() == 1  # still in queue (delivered)
        stats = q.get_stats()
        assert stats.total_delivered == 1
        assert stats.delivery_rate == 1.0

    def test_retry_on_failure(self):
        q = WebhookRetryQueue()
        q.enqueue(self._make_task())
        result = q.record_attempt("task-1", status_code=500, latency_ms=100.0, error="Internal Server Error")
        assert result.status == DeliveryStatus.RETRYING
        assert result.attempt_count == 1
        assert result.next_retry_at is not None
        assert len(result.attempts) == 1
        assert result.attempts[0].success is False

    def test_dead_letter_after_max_attempts(self):
        q = WebhookRetryQueue(max_attempts=3)
        q.enqueue(self._make_task())

        for i in range(3):
            q.record_attempt("task-1", status_code=500, latency_ms=50.0)

        assert q.queue_size() == 0
        assert q.dead_letter_size() == 1
        dl = q.get_dead_letter_tasks()
        assert dl[0].status == DeliveryStatus.DEAD_LETTER
        assert dl[0].attempt_count == 3
        stats = q.get_stats()
        assert stats.total_dead_lettered == 1

    def test_retry_not_ready_until_scheduled_time(self):
        q = WebhookRetryQueue()
        q.enqueue(self._make_task())
        q.record_attempt("task-1", status_code=502, latency_ms=30.0)

        # Task is retrying but not yet ready
        now = datetime.now(UTC)
        pending = q.get_pending(now)
        assert len(pending) == 0

        # After backoff period
        future = now + timedelta(seconds=60)
        pending = q.get_pending(future)
        assert len(pending) == 1

    def test_cancel_pending_task(self):
        q = WebhookRetryQueue()
        q.enqueue(self._make_task())
        cancelled = q.cancel("task-1")
        assert cancelled is not None
        assert cancelled.status == DeliveryStatus.CANCELLED
        assert q.queue_size() == 0

    def test_cancel_nonexistent_returns_none(self):
        q = WebhookRetryQueue()
        assert q.cancel("nonexistent") is None

    def test_replay_dead_letter(self):
        q = WebhookRetryQueue(max_attempts=1)
        q.enqueue(self._make_task())
        q.record_attempt("task-1", status_code=500, latency_ms=10.0)
        assert q.dead_letter_size() == 1

        replayed = q.replay_dead_letter("task-1")
        assert replayed is not None
        assert replayed.status == DeliveryStatus.PENDING
        assert replayed.attempt_count == 0
        assert q.queue_size() == 1
        assert q.dead_letter_size() == 0

    def test_replay_nonexistent_returns_none(self):
        q = WebhookRetryQueue()
        assert q.replay_dead_letter("nonexistent") is None

    def test_circuit_breaker_integration(self):
        q = WebhookRetryQueue(max_attempts=20)
        url = "https://broken.example.com/hook"

        for i in range(CIRCUIT_BREAKER_THRESHOLD):
            task = self._make_task(task_id=f"task-{i}", url=url)
            q.enqueue(task)
            q.record_attempt(task.task_id, status_code=500, latency_ms=10.0)

        assert q.is_circuit_open(url) is True

    def test_multiple_tasks_ordered_by_created(self):
        q = WebhookRetryQueue()
        t1 = self._make_task(task_id="older")
        t1.created_at = datetime.now(UTC) - timedelta(minutes=5)
        t2 = self._make_task(task_id="newer")
        t2.created_at = datetime.now(UTC)
        q.enqueue(t2)
        q.enqueue(t1)
        pending = q.get_pending()
        assert pending[0].task_id == "older"
        assert pending[1].task_id == "newer"

    def test_stats_avg_latency(self):
        q = WebhookRetryQueue()
        q.enqueue(self._make_task(task_id="a"))
        q.enqueue(self._make_task(task_id="b"))
        q.record_attempt("a", status_code=200, latency_ms=100.0)
        q.record_attempt("b", status_code=200, latency_ms=200.0)
        stats = q.get_stats()
        assert stats.avg_latency_ms == pytest.approx(150.0)

    def test_record_attempt_unknown_task_raises(self):
        q = WebhookRetryQueue()
        with pytest.raises(ValueError, match="not found"):
            q.record_attempt("nonexistent", status_code=200, latency_ms=10.0)

    def test_connection_error_no_status_code(self):
        q = WebhookRetryQueue()
        q.enqueue(self._make_task())
        result = q.record_attempt("task-1", status_code=None, latency_ms=5000.0, error="Connection timeout")
        assert result.status == DeliveryStatus.RETRYING
        assert result.attempts[0].error == "Connection timeout"
        assert result.attempts[0].success is False
