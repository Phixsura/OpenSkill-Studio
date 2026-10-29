import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_feature_flag import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag, FeatureFlag,
)

class TestApiFeatureFlag:
    def test_disabled_flag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="f1", name="New UI", enabled=False))
        assert svc.is_enabled("inst-1", "f1", "c1") is False

    def test_100pct_rollout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="f1", name="New UI", enabled=True, rollout_pct=100))
        assert svc.is_enabled("inst-1", "f1", "any-consumer") is True

    def test_allowlist(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="f1", name="Beta", enabled=True, rollout_pct=0, allowlist=["c1"]))
        assert svc.is_enabled("inst-1", "f1", "c1") is True
        assert svc.is_enabled("inst-1", "f1", "c2") is False

    def test_deterministic_rollout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="f1", name="Test", enabled=True, rollout_pct=50))
        results = {svc.is_enabled("inst-1", "f1", "c1") for _ in range(10)}
        assert len(results) == 1  # deterministic for same consumer

    def test_toggle(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="f1", name="Test", enabled=True, rollout_pct=100))
        svc.toggle("inst-1", "f1", False)
        assert svc.is_enabled("inst-1", "f1", "c1") is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiFeatureFlag()
        svc.create_flag("inst-1", FeatureFlag(flag_id="f1", name="Test"))
        assert len(svc.list_flags("inst-2")) == 0
