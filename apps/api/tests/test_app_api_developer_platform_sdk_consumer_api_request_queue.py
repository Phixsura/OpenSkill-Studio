"""Tests for Request Queue Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_request_queue import (
    RequestQueueManager, QueuedRequest,
)


class TestRequestQueueManager:
    def test_enqueue_and_dequeue(self):
        svc = RequestQueueManager()
        svc.enqueue(QueuedRequest("r1", "c1", "ep1"))
        result = svc.dequeue()
        assert result["request_id"] == "r1"

    def test_priority_ordering(self):
        svc = RequestQueueManager()
        svc.enqueue(QueuedRequest("r1", "c1", "ep1", priority=5))
        svc.enqueue(QueuedRequest("r2", "c1", "ep1", priority=1))
        svc.enqueue(QueuedRequest("r3", "c1", "ep1", priority=3))
        result = svc.dequeue()
        assert result["request_id"] == "r2"  # lowest priority number first

    def test_concurrency_limit(self):
        svc = RequestQueueManager()
        svc.configure(2)
        svc.enqueue(QueuedRequest("r1", "c1", "ep1"))
        svc.enqueue(QueuedRequest("r2", "c1", "ep1"))
        svc.enqueue(QueuedRequest("r3", "c1", "ep1"))
        svc.dequeue()
        svc.dequeue()
        result = svc.dequeue()
        assert result["error"] == "at_capacity"

    def test_complete_frees_slot(self):
        svc = RequestQueueManager()
        svc.configure(1)
        svc.enqueue(QueuedRequest("r1", "c1", "ep1"))
        svc.enqueue(QueuedRequest("r2", "c1", "ep1"))
        svc.dequeue()
        svc.complete("r1")
        result = svc.dequeue()
        assert result["request_id"] == "r2"

    def test_complete_failed(self):
        svc = RequestQueueManager()
        svc.enqueue(QueuedRequest("r1", "c1", "ep1"))
        svc.dequeue()
        result = svc.complete("r1", success=False)
        assert result["status"] == "failed"

    def test_stats(self):
        svc = RequestQueueManager()
        svc.configure(10)
        svc.enqueue(QueuedRequest("r1", "c1", "ep1"))
        svc.enqueue(QueuedRequest("r2", "c1", "ep1"))
        svc.dequeue()
        stats = svc.get_stats()
        assert stats["queued"] == 1
        assert stats["processing"] == 1

    def test_cancel(self):
        svc = RequestQueueManager()
        svc.enqueue(QueuedRequest("r1", "c1", "ep1"))
        result = svc.cancel("r1")
        assert result["cancelled"] is True
        assert svc.dequeue() is None

    def test_peek(self):
        svc = RequestQueueManager()
        svc.enqueue(QueuedRequest("r1", "c1", "ep1", priority=2))
        svc.enqueue(QueuedRequest("r2", "c1", "ep1", priority=1))
        peeked = svc.peek(2)
        assert peeked[0]["request_id"] == "r2"

    def test_drain(self):
        svc = RequestQueueManager()
        svc.configure(3)
        for i in range(5):
            svc.enqueue(QueuedRequest(f"r{i}", "c1", "ep1"))
        drained = svc.drain()
        assert len(drained) == 3
        assert svc.get_stats()["queued"] == 2

    def test_empty_dequeue(self):
        svc = RequestQueueManager()
        assert svc.dequeue() is None

    def test_isolation(self):
        a, b = RequestQueueManager(), RequestQueueManager()
        a.enqueue(QueuedRequest("r1", "c1", "ep1"))
        assert b.dequeue() is None
