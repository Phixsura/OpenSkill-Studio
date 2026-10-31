from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_event_aggregator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator, AggregationConfig,
)

class TestWebhookEventAggregator:
    def test_aggregate_until_full(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator()
        svc.configure("inst-1", AggregationConfig(consumer_id="c1", max_batch_size=3))
        assert svc.add_event("inst-1", "c1", {"type": "a"}) is None
        assert svc.add_event("inst-1", "c1", {"type": "b"}) is None
        batch = svc.add_event("inst-1", "c1", {"type": "c"})
        assert batch is not None and len(batch.events) == 3

    def test_manual_flush(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator()
        svc.configure("inst-1", AggregationConfig(consumer_id="c1", max_batch_size=100))
        svc.add_event("inst-1", "c1", {"type": "a"})
        batch = svc.flush("inst-1", "c1")
        assert batch is not None and len(batch.events) == 1

    def test_no_config_skips(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator()
        assert svc.add_event("inst-1", "c1", {"type": "a"}) is None

    def test_pending_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator()
        svc.configure("inst-1", AggregationConfig(consumer_id="c1", max_batch_size=10))
        svc.add_event("inst-1", "c1", {"type": "a"})
        svc.add_event("inst-1", "c1", {"type": "b"})
        assert svc.pending_count("inst-1", "c1") == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventAggregator()
        svc.configure("inst-1", AggregationConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
