"""Tests for App Task Queue — enqueue, dequeue, retry, stats."""

import pytest

from app.services.app_task_queue import AppTaskQueue, TaskStatus


class TestEnqueue:
    def test_enqueue(self):
        q = AppTaskQueue()
        t = q.enqueue("inst-1", "t1", "email.send", {"to": "user@example.com"})
        assert t.status == TaskStatus.PENDING


class TestDequeue:
    def test_priority_order(self):
        q = AppTaskQueue()
        q.enqueue("inst-1", "t1", "low", {}, priority=1)
        q.enqueue("inst-1", "t2", "high", {}, priority=10)
        t = q.dequeue("inst-1")
        assert t is not None
        assert t.task_id == "t2"

    def test_empty(self):
        q = AppTaskQueue()
        assert q.dequeue("inst-1") is None


class TestLifecycle:
    def test_complete(self):
        q = AppTaskQueue()
        q.enqueue("inst-1", "t1", "job", {})
        q.dequeue("inst-1")
        t = q.complete("inst-1", "t1")
        assert t.status == TaskStatus.COMPLETED

    def test_fail_retry(self):
        q = AppTaskQueue()
        q.enqueue("inst-1", "t1", "job", {}, max_retries=3)
        q.dequeue("inst-1")
        t = q.fail("inst-1", "t1", "timeout")
        assert t.status == TaskStatus.PENDING  # retried
        assert t.attempts == 1

    def test_fail_exhausted(self):
        q = AppTaskQueue()
        q.enqueue("inst-1", "t1", "job", {}, max_retries=1)
        q.dequeue("inst-1")
        t = q.fail("inst-1", "t1", "error")
        assert t.status == TaskStatus.FAILED


class TestStats:
    def test_stats(self):
        q = AppTaskQueue()
        q.enqueue("inst-1", "t1", "a", {})
        q.enqueue("inst-1", "t2", "b", {})
        q.dequeue("inst-1")
        s = q.stats("inst-1")
        assert s["pending"] == 1
        assert s["running"] == 1


class TestIsolation:
    def test_cross(self):
        q = AppTaskQueue()
        q.enqueue("inst-1", "t1", "job", {})
        assert q.pending_count("inst-2") == 0
