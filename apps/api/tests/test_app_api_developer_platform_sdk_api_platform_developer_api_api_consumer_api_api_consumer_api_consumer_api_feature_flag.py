import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_feature_flag import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag, FeatureFlag, ConsumerOverride,
)

class TestConsumerApiFeatureFlag:
    def test_default_enabled(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="dark_mode", name="Dark Mode", default_enabled=True))
        assert svc.is_enabled("inst-1", "c1", "dark_mode")

    def test_default_disabled(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="beta", name="Beta", default_enabled=False))
        assert not svc.is_enabled("inst-1", "c1", "beta")

    def test_override(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="beta", name="Beta", default_enabled=False))
        svc.set_override("inst-1", ConsumerOverride(consumer_id="c1", flag_id="beta", enabled=True))
        assert svc.is_enabled("inst-1", "c1", "beta")
        assert not svc.is_enabled("inst-1", "c2", "beta")  # no override

    def test_rollout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="new_ui", name="New UI", rollout_pct=100))
        assert svc.is_enabled("inst-1", "c1", "new_ui")  # 100% = everyone

    def test_consumer_flags(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="a", name="A", default_enabled=True))
        svc.create_flag("inst-1", FeatureFlag(flag_id="b", name="B", default_enabled=False))
        flags = svc.get_consumer_flags("inst-1", "c1")
        assert flags["a"] is True and flags["b"] is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="x", name="X", default_enabled=True))
        assert not svc.is_enabled("inst-2", "c1", "x")
