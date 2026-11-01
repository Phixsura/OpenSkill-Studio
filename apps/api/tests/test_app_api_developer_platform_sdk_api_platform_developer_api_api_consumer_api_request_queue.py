import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_request_queue import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue, QueuedRequest, QueueStatus,
)

class TestRequestQueue:
    def test_enqueue_and_dequeue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1", method="POST", path="/orders"))
        r = svc.dequeue("inst-1")
        assert r is not None and r.status == QueueStatus.PROCESSING

    def test_complete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1", method="GET", path="/a"))
        svc.complete("inst-1", "r1", 200)
        s = svc.stats("inst-1")
        assert s["completed"] == 1

    def test_queue_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue(max_queue_size=10)
        for i in range(10): svc.enqueue("inst-1", QueuedRequest(request_id=f"r{i}", consumer_id="c1", method="GET", path="/a"))
        with pytest.raises(ValueError, match="full"):
            svc.enqueue("inst-1", QueuedRequest(request_id="r99", consumer_id="c1", method="GET", path="/a"))

    def test_depth(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1", method="GET", path="/a"))
        svc.enqueue("inst-1", QueuedRequest(request_id="r2", consumer_id="c1", method="GET", path="/a"))
        svc.dequeue("inst-1")
        assert svc.queue_depth("inst-1") == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue()
        svc.enqueue("inst-1", QueuedRequest(request_id="r1", consumer_id="c1", method="GET", path="/a"))
        assert svc.queue_depth("inst-2") == 0
