from app.services.app_api_developer_platform_sdk_webhook_event_priority_queue import AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue

class TestEventPriorityQueue:
    def test_enqueue(self):
        q = AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue()
        e = q.enqueue("inst-1", "e1", "push", "high", "https://a.com")
        assert e.priority == "high"

    def test_priority_order(self):
        q = AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue()
        q.enqueue("inst-1", "e1", "push", "low", "https://a.com")
        q.enqueue("inst-1", "e2", "alert", "critical", "https://a.com")
        e = q.dequeue("inst-1")
        assert e.priority == "critical"

    def test_empty(self):
        q = AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue()
        assert q.dequeue("inst-1") is None

    def test_processed_count(self):
        q = AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue()
        q.enqueue("inst-1", "e1", "push", "normal", "https://a.com")
        q.dequeue("inst-1")
        assert q.processed_count("inst-1") == 1

    def test_isolation(self):
        q = AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue()
        q.enqueue("inst-1", "e1", "push", "normal", "https://a.com")
        assert q.queue_size("inst-2") == 0
