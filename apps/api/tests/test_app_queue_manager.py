"""Tests for App Queue Manager — enqueue, dequeue, priority, dead-letter."""

import pytest

from app.services.app_queue_manager import AppQueueManager, JobStatus


class TestEnqueue:
    def test_enqueue(self):
        q = AppQueueManager()
        j = q.enqueue("inst-1", "j1", "emails", {"to": "a@b.com"})
        assert j.job_id == "j1"
        assert j.status == JobStatus.PENDING
        assert j.queue_name == "emails"

    def test_duplicate(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        with pytest.raises(ValueError, match="already exists"):
            q.enqueue("inst-1", "j1", "q", {})

    def test_missing_queue_name(self):
        q = AppQueueManager()
        with pytest.raises(ValueError, match="queue_name"):
            q.enqueue("inst-1", "j1", "", {})

    def test_negative_priority(self):
        q = AppQueueManager()
        with pytest.raises(ValueError, match="priority"):
            q.enqueue("inst-1", "j1", "q", {}, priority=-1)


class TestDequeue:
    def test_dequeue_fifo(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {"n": 1}, now=1000.0)
        q.enqueue("inst-1", "j2", "q", {"n": 2}, now=1001.0)
        j = q.dequeue("inst-1", "q")
        assert j is not None
        assert j.job_id == "j1"
        assert j.status == JobStatus.PROCESSING

    def test_dequeue_by_priority(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "low", "q", {}, priority=10, now=1000.0)
        q.enqueue("inst-1", "high", "q", {}, priority=0, now=1001.0)
        j = q.dequeue("inst-1", "q")
        assert j.job_id == "high"

    def test_dequeue_empty(self):
        q = AppQueueManager()
        assert q.dequeue("inst-1", "q") is None

    def test_dequeue_skips_processing(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        q.dequeue("inst-1", "q")  # j1 now processing
        assert q.dequeue("inst-1", "q") is None


class TestCompleteJob:
    def test_complete(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        q.dequeue("inst-1", "q")
        j = q.complete_job("inst-1", "j1")
        assert j.status == JobStatus.COMPLETED
        assert j.completed_at is not None

    def test_cannot_complete_pending(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        with pytest.raises(ValueError, match="Cannot complete"):
            q.complete_job("inst-1", "j1")


class TestFailJob:
    def test_fail_retries(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {}, max_retries=3)
        q.dequeue("inst-1", "q")
        j = q.fail_job("inst-1", "j1", error="timeout")
        assert j.status == JobStatus.PENDING  # re-enqueued
        assert j.error == "timeout"

    def test_fail_to_dead_letter(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {}, max_retries=1)
        q.dequeue("inst-1", "q")  # attempt 1
        j = q.fail_job("inst-1", "j1", error="crash")
        assert j.status == JobStatus.DEAD_LETTER

    def test_cannot_fail_pending(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        with pytest.raises(ValueError, match="Cannot fail"):
            q.fail_job("inst-1", "j1")


class TestDeadLetter:
    def test_get_dead_letters(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {}, max_retries=1)
        q.dequeue("inst-1", "q")
        q.fail_job("inst-1", "j1")
        dl = q.get_dead_letters("inst-1", "q")
        assert len(dl) == 1
        assert dl[0].job_id == "j1"


class TestStats:
    def test_queue_stats(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        q.enqueue("inst-1", "j2", "q", {})
        q.dequeue("inst-1", "q")
        q.complete_job("inst-1", "j1")
        stats = q.get_queue_stats("inst-1", "q")
        assert stats.pending == 1
        assert stats.completed == 1

    def test_queue_size(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        q.enqueue("inst-1", "j2", "q", {})
        assert q.queue_size("inst-1", "q") == 2


class TestIsolation:
    def test_cross_installation(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        with pytest.raises(KeyError):
            q.get_job("inst-2", "j1")

    def test_dequeue_isolated(self):
        q = AppQueueManager()
        q.enqueue("inst-1", "j1", "q", {})
        assert q.dequeue("inst-2", "q") is None
