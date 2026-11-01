import pytest
from app.services.app_api_developer_api_api_feature_flag_manager import AppAPIDeveloperAPIApiFeatureFlagManager

class TestFeatureFlagManager:
    def test_create(self):
        m = AppAPIDeveloperAPIApiFeatureFlagManager()
        f = m.create("inst-1", "f1", "Dark Mode", enabled=True, rollout_pct=50)
        assert f.rollout_pct == 50

    def test_disabled_always_false(self):
        m = AppAPIDeveloperAPIApiFeatureFlagManager()
        m.create("inst-1", "f1", "Feature", enabled=False, rollout_pct=100)
        assert m.evaluate("inst-1", "f1", "any") is False

    def test_full_rollout(self):
        m = AppAPIDeveloperAPIApiFeatureFlagManager()
        m.create("inst-1", "f1", "Feature", enabled=True, rollout_pct=100)
        assert m.evaluate("inst-1", "f1", "any") is True

    def test_deterministic(self):
        m = AppAPIDeveloperAPIApiFeatureFlagManager()
        m.create("inst-1", "f1", "Feature", enabled=True, rollout_pct=50)
        r1 = m.evaluate("inst-1", "f1", "user-1")
        r2 = m.evaluate("inst-1", "f1", "user-1")
        assert r1 == r2

    def test_toggle(self):
        m = AppAPIDeveloperAPIApiFeatureFlagManager()
        m.create("inst-1", "f1", "Feature", enabled=True, rollout_pct=100)
        m.toggle("inst-1", "f1", False)
        assert m.evaluate("inst-1", "f1") is False

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiFeatureFlagManager()
        m.create("inst-1", "f1", "Feature")
        assert len(m.list_flags("inst-2")) == 0
