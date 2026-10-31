import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_webhook_dead_letter_queue import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue, DeadLetterEntry,
)

class TestWebhookDeadLetterQueue:
    def test_enqueue_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", DeadLetterEntry(entry_id="e1", event_id="ev1", consumer_id="c1", endpoint="/hook", payload_preview='{"test":1}', last_status_code=500, attempts=5, reason="max_retries"))
        entries = svc.list_entries("inst-1")
        assert len(entries) == 1 and entries[0].reason == "max_retries"

    def test_requeue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", DeadLetterEntry(entry_id="e1", event_id="ev1", consumer_id="c1", endpoint="/hook", payload_preview="{}", last_status_code=500, attempts=3, reason="timeout"))
        e = svc.requeue("inst-1", "e1")
        assert e.requeued is True
        with pytest.raises(ValueError, match="Already requeued"):
            svc.requeue("inst-1", "e1")

    def test_purge(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", DeadLetterEntry(entry_id="e1", event_id="ev1", consumer_id="c1", endpoint="/h", payload_preview="{}", last_status_code=500, attempts=1, reason="timeout"))
        assert svc.purge("inst-1") == 1
        assert svc.count("inst-1") == 0

    def test_by_reason(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", DeadLetterEntry(entry_id="e1", event_id="ev1", consumer_id="c1", endpoint="/h", payload_preview="{}", last_status_code=500, attempts=1, reason="timeout"))
        svc.enqueue("inst-1", DeadLetterEntry(entry_id="e2", event_id="ev2", consumer_id="c1", endpoint="/h", payload_preview="{}", last_status_code=500, attempts=5, reason="max_retries"))
        reasons = svc.by_reason("inst-1")
        assert reasons["timeout"] == 1 and reasons["max_retries"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", DeadLetterEntry(entry_id="e1", event_id="ev1", consumer_id="c1", endpoint="/h", payload_preview="{}", last_status_code=500, attempts=1, reason="timeout"))
        assert svc.count("inst-2") == 0
