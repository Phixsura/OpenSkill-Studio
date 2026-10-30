from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_priority_queue import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue, PrioritizedEvent,
)

class TestWebhookPriorityQueue:
    def test_priority_order(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue()
        svc.enqueue("inst-1", PrioritizedEvent(event_id="e1", event_type="low", consumer_id="c1", priority=5))
        svc.enqueue("inst-1", PrioritizedEvent(event_id="e2", event_type="high", consumer_id="c1", priority=1))
        result = svc.dequeue("inst-1")
        assert result.event_id == "e2"  # higher priority (lower number) first

    def test_peek(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue()
        svc.enqueue("inst-1", PrioritizedEvent(event_id="e1", event_type="x", consumer_id="c1", priority=3))
        assert svc.peek("inst-1").event_id == "e1"
        assert svc.depth("inst-1") == 1  # peek doesn't remove

    def test_empty_dequeue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue()
        assert svc.dequeue("inst-1") is None

    def test_queue_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue(max_queue_size=100)
        for i in range(100): svc.enqueue("inst-1", PrioritizedEvent(event_id=f"e{i}", event_type="x", consumer_id="c1", priority=5))
        import pytest
        with pytest.raises(ValueError, match="full"):
            svc.enqueue("inst-1", PrioritizedEvent(event_id="overflow", event_type="x", consumer_id="c1", priority=1))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue()
        svc.enqueue("inst-1", PrioritizedEvent(event_id="e1", event_type="x", consumer_id="c1", priority=5))
        assert svc.depth("inst-2") == 0
