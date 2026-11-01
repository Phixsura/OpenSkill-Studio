import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_fanout import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout, FanoutConfig, FanoutTarget,
)

class TestWebhookFanout:
    def test_fanout_to_active(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[
            FanoutTarget(target_id="t1", url="https://a.com/hook"),
            FanoutTarget(target_id="t2", url="https://b.com/hook", active=False),
        ]))
        targets = svc.fanout("inst-1", "c1")
        assert len(targets) == 1 and targets[0].delivery_count == 1

    def test_max_targets(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", max_targets=2, targets=[FanoutTarget("t1", "https://a.com")]))
        svc.add_target("inst-1", "c1", FanoutTarget("t2", "https://b.com"))
        with pytest.raises(ValueError, match="Max targets"):
            svc.add_target("inst-1", "c1", FanoutTarget("t3", "https://c.com"))

    def test_duplicate_target(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[FanoutTarget("t1", "https://a.com")]))
        with pytest.raises(ValueError, match="already exists"):
            svc.add_target("inst-1", "c1", FanoutTarget("t1", "https://b.com"))

    def test_failure_tracking(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1", targets=[FanoutTarget("t1", "https://a.com")]))
        svc.record_failure("inst-1", "c1", "t1")
        config = svc._get("inst-1", "c1")
        assert config.targets[0].failure_count == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookFanout()
        svc.configure("inst-1", FanoutConfig(consumer_id="c1"))
        assert len(svc.list_configs("inst-2")) == 0
