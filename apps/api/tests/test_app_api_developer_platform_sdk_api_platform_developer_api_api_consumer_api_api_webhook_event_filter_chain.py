import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_event_filter_chain import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain, FilterChain, FilterStep,
)

class TestWebhookEventFilterChain:
    def test_all_mode(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain()
        svc.create_chain("inst-1", FilterChain(chain_id="c1", mode="all", steps=[
            FilterStep(step_id="s1", filter_type="event_type", config={"pattern": "order.*"}),
            FilterStep(step_id="s2", filter_type="field_match", config={"field": "status", "value": "paid"}),
        ]))
        assert svc.evaluate("inst-1", "c1", "order.updated", {"status": "paid"}) is True
        assert svc.evaluate("inst-1", "c1", "order.updated", {"status": "pending"}) is False

    def test_any_mode(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain()
        svc.create_chain("inst-1", FilterChain(chain_id="c1", mode="any", steps=[
            FilterStep(step_id="s1", filter_type="event_type", config={"pattern": "order.created"}),
            FilterStep(step_id="s2", filter_type="event_type", config={"pattern": "user.created"}),
        ]))
        assert svc.evaluate("inst-1", "c1", "user.created", {}) is True

    def test_inverted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain()
        svc.create_chain("inst-1", FilterChain(chain_id="c1", steps=[
            FilterStep(step_id="s1", filter_type="event_type", config={"pattern": "internal.*"}, inverted=True),
        ]))
        assert svc.evaluate("inst-1", "c1", "internal.debug", {}) is False
        assert svc.evaluate("inst-1", "c1", "order.created", {}) is True

    def test_no_chain_passes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain()
        assert svc.evaluate("inst-1", "nonexistent", "any", {}) is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventFilterChain()
        svc.create_chain("inst-1", FilterChain(chain_id="c1", steps=[FilterStep(step_id="s1", filter_type="event_type", config={"pattern": "*"})]))
        assert len(svc.list_chains("inst-2")) == 0
