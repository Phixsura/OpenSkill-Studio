import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_webhook_fanout import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout, FanoutConfig, FanoutTarget,
)

class TestConsumerWebhookFanout:
    def test_fanout_all(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[
            FanoutTarget(target_id="t1", webhook_url="https://a.com"),
            FanoutTarget(target_id="t2", webhook_url="https://b.com"),
        ]))
        result = svc.fanout("inst-1", "c1", "order.created")
        assert result.targets_matched == 2

    def test_event_filter(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[
            FanoutTarget(target_id="t1", webhook_url="https://a.com", filter_events=["order.created"]),
            FanoutTarget(target_id="t2", webhook_url="https://b.com", filter_events=["user.updated"]),
        ]))
        result = svc.fanout("inst-1", "c1", "order.created")
        assert result.targets_matched == 1 and result.deliveries == ["t1"]

    def test_inactive_skipped(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[
            FanoutTarget(target_id="t1", webhook_url="https://a.com", active=False),
        ]))
        result = svc.fanout("inst-1", "c1", "test")
        assert result.targets_matched == 0 and result.targets_skipped == 1

    def test_max_targets(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        config = FanoutConfig(consumer_id="c1", max_targets=2, targets=[
            FanoutTarget(target_id="t1", webhook_url="https://a.com"),
            FanoutTarget(target_id="t2", webhook_url="https://b.com"),
        ])
        svc.configure("inst-1", config)
        with pytest.raises(ValueError, match="Max targets"):
            svc.add_target("inst-1", "c1", FanoutTarget(target_id="t3", webhook_url="https://c.com"))

    def test_https_required(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[FanoutTarget(target_id="t1", webhook_url="http://insecure.com")]))

    def test_remove_target(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[FanoutTarget(target_id="t1", webhook_url="https://a.com")]))
        svc.remove_target("inst-1", "c1", "t1")
        assert len(svc.get_config("inst-1", "c1").targets) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[FanoutTarget(target_id="t1", webhook_url="https://a.com")]))
        assert svc.get_config("inst-2", "c1") is None
