from app.services.app_api_developer_platform_sdk_api_platform_developer_api_webhook_filter_rule import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule, FilterRule,
)

class TestWebhookFilterRule:
    def test_include_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule()
        svc.add_rule("inst-1", "c1", FilterRule(rule_id="r1", event_type="order.*", action="include"))
        r = svc.evaluate("inst-1", "c1", "order.created", {})
        assert r.delivered is True

    def test_exclude_wins(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule()
        svc.add_rule("inst-1", "c1", FilterRule(rule_id="r1", event_type="order.*", action="include"))
        svc.add_rule("inst-1", "c1", FilterRule(rule_id="r2", event_type="order.deleted", action="exclude"))
        r = svc.evaluate("inst-1", "c1", "order.deleted", {})
        assert r.delivered is False

    def test_field_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule()
        svc.add_rule("inst-1", "c1", FilterRule(rule_id="r1", event_type="user.*", action="include", field_match={"role": "^admin$"}))
        assert svc.evaluate("inst-1", "c1", "user.updated", {"role": "admin"}).delivered is True
        assert svc.evaluate("inst-1", "c1", "user.updated", {"role": "member"}).delivered is False

    def test_no_rules_delivers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule()
        r = svc.evaluate("inst-1", "c1", "any.event", {})
        assert r.delivered is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookFilterRule()
        svc.add_rule("inst-1", "c1", FilterRule(rule_id="r1", event_type="*", action="include"))
        assert svc.rule_count("inst-2") == 0
