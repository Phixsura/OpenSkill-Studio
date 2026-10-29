import pytest
from app.services.app_api_developer_api_api_request_priority_queue import AppAPIDeveloperAPIApiRequestPriorityQueue

class TestRequestPriorityQueue:
    def test_enqueue(self):
        q = AppAPIDeveloperAPIApiRequestPriorityQueue()
        r = q.enqueue("inst-1", "r1", "high", "/api/users")
        assert r.priority == "high"

    def test_priority_ordering(self):
        q = AppAPIDeveloperAPIApiRequestPriorityQueue()
        q.enqueue("inst-1", "r1", "low", "/api")
        q.enqueue("inst-1", "r2", "critical", "/api")
        q.enqueue("inst-1", "r3", "normal", "/api")
        first = q.dequeue("inst-1")
        assert first.priority == "critical"

    def test_invalid_priority(self):
        q = AppAPIDeveloperAPIApiRequestPriorityQueue()
        with pytest.raises(ValueError):
            q.enqueue("inst-1", "r1", "ultra", "/api")

    def test_empty_dequeue(self):
        q = AppAPIDeveloperAPIApiRequestPriorityQueue()
        assert q.dequeue("inst-1") is None

    def test_distribution(self):
        q = AppAPIDeveloperAPIApiRequestPriorityQueue()
        q.enqueue("inst-1", "r1", "high", "/api")
        q.enqueue("inst-1", "r2", "high", "/api")
        q.enqueue("inst-1", "r3", "low", "/api")
        dist = q.priority_distribution("inst-1")
        assert dist["high"] == 2
        assert dist["low"] == 1

    def test_isolation(self):
        q = AppAPIDeveloperAPIApiRequestPriorityQueue()
        q.enqueue("inst-1", "r1", "normal", "/api")
        assert q.queue_size("inst-2") == 0
