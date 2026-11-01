"""Tests for Consumer Usage Leaderboard service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_usage_leaderboard import UsageLeaderboard


class TestUsageLeaderboard:
    def test_record_and_rank(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 5000)
        svc.record_usage("c2", 20000)
        ranking = svc.get_ranking()
        assert ranking[0]["consumer_id"] == "c2"
        assert ranking[0]["rank"] == 1

    def test_tier_assignment(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 500)
        svc.record_usage("c2", 50000)
        ranking = svc.get_ranking()
        tiers = {r["consumer_id"]: r["tier"] for r in ranking}
        assert tiers["c1"] == "bronze"
        assert tiers["c2"] == "gold"

    def test_badge_award(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 100)
        result = svc.award_badge("c1", "early_adopter")
        assert result["awarded"] is True
        profile = svc.get_consumer_profile("c1")
        assert "early_adopter" in profile["badges"]

    def test_duplicate_badge(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 100)
        svc.award_badge("c1", "badge1")
        result = svc.award_badge("c1", "badge1")
        assert result["awarded"] is False

    def test_uptime_affects_points(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 100)
        svc.record_usage("c2", 100)
        svc.set_uptime("c1", 365)
        ranking = svc.get_ranking()
        assert ranking[0]["consumer_id"] == "c1"  # higher points from uptime

    def test_consumer_profile(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 15000, endpoints_used=10)
        svc.set_uptime("c1", 30)
        profile = svc.get_consumer_profile("c1")
        assert profile["tier"] == "gold"
        assert profile["rank"] == 1
        assert profile["next_tier_at"] == 100000

    def test_profile_not_found(self):
        svc = UsageLeaderboard()
        assert svc.get_consumer_profile("missing") is None

    def test_stats(self):
        svc = UsageLeaderboard()
        svc.record_usage("c1", 500)
        svc.record_usage("c2", 50000)
        svc.award_badge("c1", "b1")
        stats = svc.get_stats()
        assert stats["total_consumers"] == 2
        assert stats["total_badges_awarded"] == 1

    def test_negative_requests(self):
        svc = UsageLeaderboard()
        with pytest.raises(ValueError):
            svc.record_usage("c1", -10)

    def test_isolation(self):
        a, b = UsageLeaderboard(), UsageLeaderboard()
        a.record_usage("c1", 1000)
        assert b.get_ranking() == []
