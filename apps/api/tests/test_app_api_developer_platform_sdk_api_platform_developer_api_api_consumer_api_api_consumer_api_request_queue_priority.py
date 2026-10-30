import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_request_queue_priority import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority, PrioritizedRequest,
)

class TestRequestQueuePriority:
    def test_priority_order(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority()
        svc.enqueue("inst-1", PrioritizedRequest(request_id="r1", consumer_id="c1", endpoint="/a", priority=5))
        svc.enqueue("inst-1", PrioritizedRequest(request_id="r2", consumer_id="c1", endpoint="/b", priority=1))
        assert svc.dequeue("inst-1").request_id == "r2"

    def test_fifo_same_priority(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority()
        svc.enqueue("inst-1", PrioritizedRequest(request_id="r1", consumer_id="c1", endpoint="/a", priority=3))
        svc.enqueue("inst-1", PrioritizedRequest(request_id="r2", consumer_id="c1", endpoint="/b", priority=3))
        assert svc.dequeue("inst-1").request_id == "r1"

    def test_empty_dequeue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority()
        assert svc.dequeue("inst-1") is None

    def test_queue_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority(max_queue=100)
        for i in range(100): svc.enqueue("inst-1", PrioritizedRequest(request_id=f"r{i}", consumer_id="c1", endpoint="/a", priority=5))
        with pytest.raises(ValueError, match="full"):
            svc.enqueue("inst-1", PrioritizedRequest(request_id="overflow", consumer_id="c1", endpoint="/a", priority=1))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority()
        svc.enqueue("inst-1", PrioritizedRequest(request_id="r1", consumer_id="c1", endpoint="/a", priority=3))
        assert svc.depth("inst-2") == 0
