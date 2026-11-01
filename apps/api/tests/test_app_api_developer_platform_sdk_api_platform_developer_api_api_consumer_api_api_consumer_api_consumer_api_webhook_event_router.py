import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_event_router import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter, RoutingRule,
)

class TestConsumerApiWebhookEventRouter:
    def test_exact_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter()
        svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r1", event_pattern="order.created", webhook_url="https://hook1.com"))
        result = svc.route("inst-1", "c1", "order.created")
        assert len(result.matched_rules) == 1

    def test_wildcard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter()
        svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r1", event_pattern="order.*", webhook_url="https://hook1.com"))
        assert len(svc.route("inst-1", "c1", "order.updated").matched_rules) == 1
        assert svc.route("inst-1", "c1", "user.created").unmatched

    def test_priority_ordering(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter()
        svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r1", event_pattern="*", webhook_url="https://low.com", priority=1))
        svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r2", event_pattern="*", webhook_url="https://high.com", priority=10))
        result = svc.route("inst-1", "c1", "any.event")
        assert result.matched_rules[0].webhook_url == "https://high.com"

    def test_inactive_skipped(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter()
        svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r1", event_pattern="*", webhook_url="https://x.com", active=False))
        assert svc.route("inst-1", "c1", "test").unmatched

    def test_https_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r1", event_pattern="*", webhook_url="http://insecure.com"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookEventRouter()
        svc.add_rule("inst-1", "c1", RoutingRule(rule_id="r1", event_pattern="*", webhook_url="https://x.com"))
        assert svc.route("inst-2", "c1", "test").unmatched
