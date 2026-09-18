"""Endorsement leaderboard tests — pure logic, no DB needed."""

from app.talent.services.endorsement_leaderboard import (
    CapabilityLeaderboardEntry,
    EndorsementStats,
    LeaderboardEntry,
)


class TestLeaderboardEntry:
    def test_structure(self):
        entry = LeaderboardEntry(
            user_id="u1",
            total_endorsements=10,
            unique_endorsers=5,
        )
        assert entry.user_id == "u1"
        assert entry.total_endorsements == 10
        assert entry.unique_endorsers == 5

    def test_frozen(self):
        entry = LeaderboardEntry(user_id="u1", total_endorsements=1, unique_endorsers=1)
        try:
            entry.user_id = "u2"  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass


class TestCapabilityLeaderboardEntry:
    def test_structure(self):
        entry = CapabilityLeaderboardEntry(
            capability_id="c1",
            capability_name="Python",
            endorsement_count=20,
            unique_users=15,
        )
        assert entry.capability_id == "c1"
        assert entry.capability_name == "Python"
        assert entry.endorsement_count == 20
        assert entry.unique_users == 15


class TestEndorsementStats:
    def test_structure(self):
        stats = EndorsementStats(
            total_endorsements=100,
            total_endorsers=30,
            total_endorsed_users=25,
            avg_per_user=4.0,
        )
        assert stats.total_endorsements == 100
        assert stats.total_endorsers == 30
        assert stats.total_endorsed_users == 25
        assert stats.avg_per_user == 4.0

    def test_zero_stats(self):
        stats = EndorsementStats(
            total_endorsements=0,
            total_endorsers=0,
            total_endorsed_users=0,
            avg_per_user=0.0,
        )
        assert stats.total_endorsements == 0
        assert stats.avg_per_user == 0.0

    def test_avg_calculation(self):
        # 50 endorsements / 10 users = 5.0 avg
        stats = EndorsementStats(
            total_endorsements=50,
            total_endorsers=20,
            total_endorsed_users=10,
            avg_per_user=5.0,
        )
        assert stats.avg_per_user == 5.0

    def test_frozen(self):
        stats = EndorsementStats(
            total_endorsements=1,
            total_endorsers=1,
            total_endorsed_users=1,
            avg_per_user=1.0,
        )
        try:
            stats.total_endorsements = 99  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass
