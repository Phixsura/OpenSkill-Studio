import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_dead_letter_queue import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue, DeadLetterEntry,
)

class TestWebhookDeadLetterQueue:
    def _now(self):
        return datetime(2026, 6, 1)

    def _entry(self, eid: str = "e1", consumer: str = "c1"):
        return DeadLetterEntry(entry_id=eid, webhook_id="wh1", consumer_id=consumer, event_type="order.created", payload='{"id":"123"}', last_error="timeout", attempts=5, first_failed_at=self._now(), last_failed_at=self._now())

    def test_enqueue_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", self._entry())
        assert svc.get("inst-1", "e1").event_type == "order.created"

    def test_requeue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", self._entry())
        svc.requeue("inst-1", "e1")
        assert svc.get("inst-1", "e1").status == "requeued"

    def test_discard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", self._entry())
        svc.discard("inst-1", "e1")
        assert svc.get("inst-1", "e1").status == "discarded"

    def test_list_pending(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", self._entry("e1"))
        svc.enqueue("inst-1", self._entry("e2"))
        svc.discard("inst-1", "e2")
        pending = svc.list_pending("inst-1")
        assert len(pending) == 1 and pending[0].entry_id == "e1"

    def test_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", self._entry("e1"))
        svc.enqueue("inst-1", self._entry("e2"))
        svc.requeue("inst-1", "e2")
        counts = svc.count("inst-1")
        assert counts["pending"] == 1 and counts["requeued"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeadLetterQueue()
        svc.enqueue("inst-1", self._entry())
        assert svc.get("inst-2", "e1") is None
