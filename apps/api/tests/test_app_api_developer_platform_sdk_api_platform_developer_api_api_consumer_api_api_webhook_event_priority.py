from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_event_priority import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority, EventPriorityRule,
)

class TestWebhookEventPriority:
    def test_exact_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority()
        svc.add_rule("inst-1", "c1", EventPriorityRule(rule_id="r1", event_pattern="payment.failed", priority=1))
        p = svc.get_priority("inst-1", "c1", "payment.failed")
        assert p.priority == 1

    def test_glob_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority()
        svc.add_rule("inst-1", "c1", EventPriorityRule(rule_id="r1", event_pattern="order.*", priority=2))
        p = svc.get_priority("inst-1", "c1", "order.created")
        assert p.priority == 2

    def test_default_medium(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority()
        p = svc.get_priority("inst-1", "c1", "unknown.event")
        assert p.priority == 3

    def test_highest_priority_wins(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority()
        svc.add_rule("inst-1", "c1", EventPriorityRule(rule_id="r1", event_pattern="*", priority=5))
        svc.add_rule("inst-1", "c1", EventPriorityRule(rule_id="r2", event_pattern="order.*", priority=1))
        p = svc.get_priority("inst-1", "c1", "order.created")
        assert p.priority == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventPriority()
        svc.add_rule("inst-1", "c1", EventPriorityRule(rule_id="r1", event_pattern="*", priority=3))
        assert svc.rule_count("inst-2") == 0
