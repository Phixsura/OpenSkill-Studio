"""Tests for App Feature Usage — recording, stats, adoption, ranking."""

import pytest

from app.services.app_feature_usage import AppFeatureUsage


class TestRecordUsage:
    def test_record(self):
        u = AppFeatureUsage()
        u.record_usage("inst-1", "dashboard", "user-1", now=1000.0)
        stats = u.get_stats("inst-1", "dashboard")
        assert stats.unique_users == 1
        assert stats.total_uses == 1

    def test_multiple_uses(self):
        u = AppFeatureUsage()
        u.record_usage("inst-1", "dashboard", "user-1")
        u.record_usage("inst-1", "dashboard", "user-1")
        u.record_usage("inst-1", "dashboard", "user-2")
        stats = u.get_stats("inst-1", "dashboard")
        assert stats.unique_users == 2
        assert stats.total_uses == 3

    def test_missing_feature(self):
        u = AppFeatureUsage()
        with pytest.raises(ValueError, match="feature_id"):
            u.record_usage("inst-1", "", "user-1")


class TestAdoption:
    def test_adoption_rate(self):
        u = AppFeatureUsage()
        # 4 total users
        for uid in ["u1", "u2", "u3", "u4"]:
            u.record_usage("inst-1", "basic", uid)
        # Only 2 use advanced
        u.record_usage("inst-1", "advanced", "u1")
        u.record_usage("inst-1", "advanced", "u2")
        stats = u.get_stats("inst-1", "advanced")
        assert stats.adoption_pct == 50.0

    def test_zero_users(self):
        u = AppFeatureUsage()
        stats = u.get_stats("inst-1", "nope")
        assert stats.adoption_pct == 0.0


class TestRanking:
    def test_most_used(self):
        u = AppFeatureUsage()
        for _ in range(10):
            u.record_usage("inst-1", "popular", "u1")
        for _ in range(3):
            u.record_usage("inst-1", "niche", "u1")
        top = u.most_used("inst-1")
        assert top[0].feature_id == "popular"

    def test_least_adopted(self):
        u = AppFeatureUsage()
        for uid in ["u1", "u2", "u3"]:
            u.record_usage("inst-1", "common", uid)
        u.record_usage("inst-1", "rare", "u1")
        bottom = u.least_adopted("inst-1")
        assert bottom[0].feature_id == "rare"


class TestGetAll:
    def test_all_stats(self):
        u = AppFeatureUsage()
        u.record_usage("inst-1", "a", "u1")
        u.record_usage("inst-1", "b", "u1")
        stats = u.get_all_stats("inst-1")
        assert len(stats) == 2


class TestIsolation:
    def test_cross_installation(self):
        u = AppFeatureUsage()
        u.record_usage("inst-1", "feat", "u1")
        stats = u.get_stats("inst-2", "feat")
        assert stats.unique_users == 0
