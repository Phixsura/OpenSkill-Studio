import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_request_throttle_queue import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue, QueuedRequest, ThrottleConfig,
)

class TestConsumerApiRequestThrottleQueue:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_enqueue_and_dequeue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1", priority=1, queued_at=self._now()))
        req = svc.dequeue("inst-1", "c1")
        assert req is not None and req.request_id == "r1" and req.status == "processing"

    def test_priority_ordering(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="low", consumer_id="c1", priority=1))
        svc.enqueue("inst-1", QueuedRequest(request_id="high", consumer_id="c1", priority=10))
        req = svc.dequeue("inst-1", "c1")
        assert req.request_id == "high"

    def test_dropped_when_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue()
        svc.configure("inst-1", ThrottleConfig(consumer_id="c1", max_queue_size=2))
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1"))
        svc.enqueue("inst-1", QueuedRequest(request_id="r2", consumer_id="c1"))
        dropped = svc.enqueue("inst-1", QueuedRequest(request_id="r3", consumer_id="c1"))
        assert dropped.status == "dropped"

    def test_complete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1"))
        svc.dequeue("inst-1", "c1")
        svc.complete("inst-1", "c1", "r1")
        stats = svc.get_stats("inst-1", "c1")
        assert stats.completed == 1 and stats.processing == 0

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue()
        svc.configure("inst-1", ThrottleConfig(consumer_id="c1", max_queue_size=10))
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1"))
        stats = svc.get_stats("inst-1", "c1")
        assert stats.queued == 1 and stats.max_queue_size == 10

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1"))
        assert svc.dequeue("inst-2", "c1") is None
