import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_webhook_content_filter import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter, ContentFilter, ContentFilterRule,
)

class TestWebhookContentFilter:
    def test_all_match(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        svc.set_filter("inst-1", "c1", ContentFilter(filter_id="f1", webhook_id="w1", match_mode="all", rules=[
            ContentFilterRule(rule_id="r1", field_path="status", operator="equals", value="active"),
            ContentFilterRule(rule_id="r2", field_path="type", operator="equals", value="order"),
        ]))
        result = svc.evaluate("inst-1", "c1", "w1", {"status": "active", "type": "order"})
        assert result.passed and result.matched_rules == 2

    def test_any_match(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        svc.set_filter("inst-1", "c1", ContentFilter(filter_id="f1", webhook_id="w1", match_mode="any", rules=[
            ContentFilterRule(rule_id="r1", field_path="priority", operator="equals", value="high"),
            ContentFilterRule(rule_id="r2", field_path="priority", operator="equals", value="critical"),
        ]))
        result = svc.evaluate("inst-1", "c1", "w1", {"priority": "critical"})
        assert result.passed

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        svc.set_filter("inst-1", "c1", ContentFilter(filter_id="f1", webhook_id="w1", rules=[
            ContentFilterRule(rule_id="r1", field_path="status", operator="equals", value="active"),
        ]))
        result = svc.evaluate("inst-1", "c1", "w1", {"status": "inactive"})
        assert not result.passed

    def test_contains(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        svc.set_filter("inst-1", "c1", ContentFilter(filter_id="f1", webhook_id="w1", rules=[
            ContentFilterRule(rule_id="r1", field_path="message", operator="contains", value="error"),
        ]))
        assert svc.evaluate("inst-1", "c1", "w1", {"message": "an error occurred"}).passed

    def test_exists_not_exists(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        svc.set_filter("inst-1", "c1", ContentFilter(filter_id="f1", webhook_id="w1", rules=[
            ContentFilterRule(rule_id="r1", field_path="data", operator="exists"),
            ContentFilterRule(rule_id="r2", field_path="error", operator="not_exists"),
        ]))
        assert svc.evaluate("inst-1", "c1", "w1", {"data": "x"}).passed

    def test_no_filter_passes(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        assert svc.evaluate("inst-1", "c1", "w1", {"anything": True}).passed

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerWebhookContentFilter()
        svc.set_filter("inst-1", "c1", ContentFilter(filter_id="f1", webhook_id="w1", rules=[ContentFilterRule(rule_id="r1", field_path="x", operator="exists")]))
        assert svc.get_filter("inst-2", "c1", "w1") is None
