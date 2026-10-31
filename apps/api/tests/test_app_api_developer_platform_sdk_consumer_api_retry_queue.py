"""Tests for Consumer Webhook Retry Queue service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_retry_queue import (
    RetryQueue, FailedDelivery,
)


class TestRetryQueue:
    def _fd(self, did="d1", wid="wh1", error="timeout"):
        return FailedDelivery(did, wid, "order.created", {"id": 1}, error)

    def test_enqueue(self):
        svc = RetryQueue()
        result = svc.enqueue(self._fd())
        assert result["status"] == "pending"
        assert result["attempts"] == 1

    def test_retry_success(self):
        svc = RetryQueue()
        svc.enqueue(self._fd())
        result = svc.retry("d1", success=True)
        assert result["status"] == "succeeded"

    def test_retry_failure(self):
        svc = RetryQueue()
        svc.enqueue(self._fd())
        result = svc.retry("d1", success=False)
        assert result["status"] == "retrying"
        assert result["attempts"] == 2

    def test_dead_after_max_attempts(self):
        svc = RetryQueue()
        svc.enqueue(FailedDelivery("d1", "wh1", "test", {}, "err", max_attempts=3))
        svc.retry("d1")  # attempt 2
        result = svc.retry("d1")  # attempt 3 -> dead
        assert result["status"] == "dead"

    def test_cannot_retry_dead(self):
        svc = RetryQueue()
        svc.enqueue(FailedDelivery("d1", "wh1", "test", {}, "err", max_attempts=1))
        svc.enqueue(self._fd("d1"))  # attempt 2 -> dead (was max 1 + re-enqueue)
        # Force dead
        svc._queue["d1"].status = "dead"
        with pytest.raises(ValueError):
            svc.retry("d1")

    def test_resurrect(self):
        svc = RetryQueue()
        svc.enqueue(FailedDelivery("d1", "wh1", "test", {}, "err", max_attempts=1))
        svc._queue["d1"].status = "dead"
        result = svc.resurrect("d1")
        assert result["resurrected"] is True
        assert svc._queue["d1"].status == "pending"

    def test_get_pending(self):
        svc = RetryQueue()
        svc.enqueue(self._fd("d1"))
        svc.enqueue(self._fd("d2"))
        svc.enqueue(self._fd("d3"))
        svc.retry("d3", success=True)
        pending = svc.get_pending()
        assert len(pending) == 2

    def test_get_dead_letters(self):
        svc = RetryQueue()
        svc.enqueue(FailedDelivery("d1", "wh1", "test", {}, "err", max_attempts=1))
        svc._queue["d1"].status = "dead"
        dead = svc.get_dead_letters()
        assert len(dead) == 1

    def test_purge_succeeded(self):
        svc = RetryQueue()
        svc.enqueue(self._fd("d1"))
        svc.enqueue(self._fd("d2"))
        svc.retry("d1", success=True)
        result = svc.purge_succeeded()
        assert result["purged"] == 1
        assert svc.get_stats()["total"] == 1

    def test_stats(self):
        svc = RetryQueue()
        svc.enqueue(self._fd("d1"))
        svc.enqueue(self._fd("d2"))
        svc.retry("d1", success=True)
        stats = svc.get_stats()
        assert stats["succeeded"] == 1
        assert stats["pending"] == 1

    def test_isolation(self):
        a, b = RetryQueue(), RetryQueue()
        a.enqueue(self._fd())
        assert b.get_stats()["total"] == 0
