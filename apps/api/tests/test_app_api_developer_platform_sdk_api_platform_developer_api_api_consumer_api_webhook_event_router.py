from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_event_router import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter, RoutingConfig, RoutingRule,
)

class TestWebhookEventRouter:
    def test_route_by_pattern(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter()
        svc.configure("inst-1", RoutingConfig(consumer_id="c1", rules=[
            RoutingRule(rule_id="r1", event_pattern="order.*", target_url="https://orders.example.com/hook"),
            RoutingRule(rule_id="r2", event_pattern="user.*", target_url="https://users.example.com/hook"),
        ], default_url="https://default.example.com/hook"))
        assert svc.route("inst-1", "c1", "order.created") == "https://orders.example.com/hook"
        assert svc.route("inst-1", "c1", "user.updated") == "https://users.example.com/hook"

    def test_default_fallback(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter()
        svc.configure("inst-1", RoutingConfig(consumer_id="c1", default_url="https://default.com/hook"))
        assert svc.route("inst-1", "c1", "unknown.event") == "https://default.com/hook"

    def test_no_config(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter()
        assert svc.route("inst-1", "c1", "any") is None

    def test_priority(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter()
        svc.configure("inst-1", RoutingConfig(consumer_id="c1", rules=[
            RoutingRule(rule_id="r1", event_pattern="*", target_url="https://catch-all.com", priority=0),
            RoutingRule(rule_id="r2", event_pattern="order.*", target_url="https://orders.com", priority=10),
        ]))
        assert svc.route("inst-1", "c1", "order.created") == "https://orders.com"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookEventRouter()
        svc.configure("inst-1", RoutingConfig(consumer_id="c1", default_url="https://x.com"))
        assert len(svc.list_configs("inst-2")) == 0
