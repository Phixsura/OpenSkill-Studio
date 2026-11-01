"""Tests for Endpoint Feature Flag service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_feature_flag import (
    FeatureFlagManager, FeatureFlag,
)


class TestFeatureFlagManager:
    def test_create_and_evaluate_disabled(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "New UI", enabled=False))
        result = svc.evaluate("f1", "c1")
        assert result["active"] is False
        assert result["reason"] == "disabled"

    def test_full_rollout(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "Feature", enabled=True, rollout_pct=100))
        assert svc.evaluate("f1", "c1")["active"] is True

    def test_zero_rollout(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "Feature", enabled=True, rollout_pct=0))
        assert svc.evaluate("f1", "c1")["active"] is False

    def test_allowlist(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "Beta", enabled=True, rollout_pct=0))
        svc.add_to_allowlist("f1", "vip")
        assert svc.evaluate("f1", "vip")["active"] is True
        assert svc.evaluate("f1", "regular")["active"] is False

    def test_denylist(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "Feature", enabled=True, rollout_pct=100,
                                     denylist=["blocked"]))
        assert svc.evaluate("f1", "blocked")["active"] is False
        assert svc.evaluate("f1", "normal")["active"] is True

    def test_deterministic_rollout(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "Test", enabled=True, rollout_pct=50))
        r1 = svc.evaluate("f1", "user-abc")
        r2 = svc.evaluate("f1", "user-abc")
        assert r1["active"] == r2["active"]  # deterministic

    def test_toggle(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "X", enabled=False))
        svc.toggle("f1", True)
        flags = svc.list_flags()
        assert flags[0]["enabled"] is True

    def test_set_rollout(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "X", enabled=True, rollout_pct=10))
        svc.set_rollout("f1", 80)
        flags = svc.list_flags()
        assert flags[0]["rollout_pct"] == 80

    def test_stats(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "X", enabled=True, rollout_pct=100))
        svc.evaluate("f1", "c1")
        svc.evaluate("f1", "c2")
        stats = svc.get_stats("f1")
        assert stats["total_evaluations"] == 2
        assert stats["active_count"] == 2

    def test_duplicate_flag(self):
        svc = FeatureFlagManager()
        svc.create_flag(FeatureFlag("f1", "X"))
        with pytest.raises(ValueError):
            svc.create_flag(FeatureFlag("f1", "Y"))

    def test_not_found(self):
        svc = FeatureFlagManager()
        assert svc.evaluate("missing", "c1")["reason"] == "not_found"

    def test_isolation(self):
        a, b = FeatureFlagManager(), FeatureFlagManager()
        a.create_flag(FeatureFlag("f1", "X", enabled=True, rollout_pct=100))
        assert b.evaluate("f1", "c1")["reason"] == "not_found"
