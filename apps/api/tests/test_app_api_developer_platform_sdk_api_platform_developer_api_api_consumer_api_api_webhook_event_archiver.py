from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_event_archiver import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver, ArchivedEvent,
)

class TestWebhookEventArchiver:
    def test_archive_and_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver()
        svc.archive("inst-1", ArchivedEvent(event_id="e1", event_type="order.created", consumer_id="c1", payload_hash="abc", size_bytes=512))
        results = svc.search("inst-1", event_type="order.created")
        assert len(results) == 1

    def test_filter_by_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver()
        svc.archive("inst-1", ArchivedEvent(event_id="e1", event_type="x", consumer_id="c1", payload_hash="a"))
        svc.archive("inst-1", ArchivedEvent(event_id="e2", event_type="x", consumer_id="c2", payload_hash="b"))
        assert len(svc.search("inst-1", consumer_id="c1")) == 1

    def test_total_size(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver()
        svc.archive("inst-1", ArchivedEvent(event_id="e1", event_type="x", consumer_id="c1", payload_hash="a", size_bytes=1024))
        svc.archive("inst-1", ArchivedEvent(event_id="e2", event_type="x", consumer_id="c1", payload_hash="b", size_bytes=2048))
        assert svc.total_size_bytes("inst-1") == 3072

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver(max_archive_size=1000)
        for i in range(1500): svc.archive("inst-1", ArchivedEvent(event_id=f"e{i}", event_type="x", consumer_id="c1", payload_hash=f"h{i}"))
        assert svc.total_archived("inst-1") == 1000

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventArchiver()
        svc.archive("inst-1", ArchivedEvent(event_id="e1", event_type="x", consumer_id="c1", payload_hash="a"))
        assert svc.total_archived("inst-2") == 0
