import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_request_priority_queue import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue, PriorityRequest,
)

class TestConsumerApiRequestPriorityQueue:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_priority_order(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue()
        svc.enqueue("inst-1", PriorityRequest(request_id="low", consumer_id="c1", endpoint="/api", priority=1, enqueued_at=self._now()))
        svc.enqueue("inst-1", PriorityRequest(request_id="high", consumer_id="c2", endpoint="/api", priority=10, enqueued_at=self._now()))
        req = svc.dequeue("inst-1")
        assert req.request_id == "high"

    def test_fifo_same_priority(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue()
        from datetime import timedelta
        svc.enqueue("inst-1", PriorityRequest(request_id="first", consumer_id="c1", endpoint="/api", priority=5, enqueued_at=self._now()))
        svc.enqueue("inst-1", PriorityRequest(request_id="second", consumer_id="c1", endpoint="/api", priority=5, enqueued_at=self._now() + timedelta(seconds=1)))
        req = svc.dequeue("inst-1")
        assert req.request_id == "first"

    def test_queue_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue(max_size=2)
        svc.enqueue("inst-1", PriorityRequest(request_id="r1", consumer_id="c1", endpoint="/api", enqueued_at=self._now()))
        svc.enqueue("inst-1", PriorityRequest(request_id="r2", consumer_id="c1", endpoint="/api", enqueued_at=self._now()))
        with pytest.raises(ValueError, match="Queue full"):
            svc.enqueue("inst-1", PriorityRequest(request_id="r3", consumer_id="c1", endpoint="/api", enqueued_at=self._now()))

    def test_get_position(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue()
        svc.enqueue("inst-1", PriorityRequest(request_id="r1", consumer_id="c1", endpoint="/api", priority=10, enqueued_at=self._now()))
        svc.enqueue("inst-1", PriorityRequest(request_id="r2", consumer_id="c1", endpoint="/api", priority=1, enqueued_at=self._now()))
        pos = svc.get_position("inst-1", "r2")
        assert pos is not None and pos.position == 2

    def test_processed_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue()
        svc.enqueue("inst-1", PriorityRequest(request_id="r1", consumer_id="c1", endpoint="/api", enqueued_at=self._now()))
        svc.dequeue("inst-1")
        assert svc.processed_count("inst-1") == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue()
        svc.enqueue("inst-1", PriorityRequest(request_id="r1", consumer_id="c1", endpoint="/api", enqueued_at=self._now()))
        assert svc.size("inst-2") == 0
