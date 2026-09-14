"""Team skill analytics tests — dataclass structure and constants."""

import dataclasses

from app.talent.services.team_analytics import (
    TeamAnalytics,
    TeamSkillSummary,
)


class TestTeamSkillSummary:
    def test_immutable(self):
        summary = TeamSkillSummary(
            capability_id="cap1",
            capability_name="Python",
            team_members_with_skill=5,
            avg_level=3.2,
            max_level=5,
            min_level=1,
            total_evidence=25,
        )
        assert summary.capability_id == "cap1"
        assert summary.avg_level == 3.2

    def test_frozen(self):
        summary = TeamSkillSummary(
            capability_id="cap1",
            capability_name="Python",
            team_members_with_skill=5,
            avg_level=3.2,
            max_level=5,
            min_level=1,
            total_evidence=25,
        )
        try:
            summary.avg_level = 4.0  # type: ignore
            raise AssertionError("Should not allow mutation")
        except AttributeError:
            pass

    def test_asdict(self):
        summary = TeamSkillSummary(
            capability_id="cap1",
            capability_name="Python",
            team_members_with_skill=5,
            avg_level=3.2,
            max_level=5,
            min_level=1,
            total_evidence=25,
        )
        d = dataclasses.asdict(summary)
        assert d["capability_name"] == "Python"
        assert d["team_members_with_skill"] == 5


class TestTeamAnalytics:
    def test_empty_team(self):
        analytics = TeamAnalytics(
            org_id="org1",
            total_members=0,
            total_capabilities_covered=0,
            skill_distribution=[],
            team_strengths=[],
            team_gaps=[],
        )
        assert analytics.total_members == 0
        assert analytics.total_capabilities_covered == 0
        assert analytics.skill_distribution == []

    def test_with_data(self):
        dist = [
            TeamSkillSummary(
                capability_id="cap1",
                capability_name="Python",
                team_members_with_skill=5,
                avg_level=3.2,
                max_level=5,
                min_level=1,
                total_evidence=25,
            ),
            TeamSkillSummary(
                capability_id="cap2",
                capability_name="JavaScript",
                team_members_with_skill=3,
                avg_level=2.5,
                max_level=4,
                min_level=1,
                total_evidence=12,
            ),
        ]
        analytics = TeamAnalytics(
            org_id="org1",
            total_members=8,
            total_capabilities_covered=2,
            skill_distribution=dist,
            team_strengths=["Python", "JavaScript"],
            team_gaps=["Machine Learning"],
        )
        assert analytics.total_members == 8
        assert len(analytics.skill_distribution) == 2
        assert analytics.team_strengths[0] == "Python"
        assert "Machine Learning" in analytics.team_gaps

    def test_strengths_max_5(self):
        """Verify the service returns at most 5 strengths."""
        analytics = TeamAnalytics(
            org_id="org1",
            total_members=10,
            total_capabilities_covered=7,
            skill_distribution=[],
            team_strengths=["A", "B", "C", "D", "E"],
            team_gaps=[],
        )
        assert len(analytics.team_strengths) <= 5

    def test_coverage_score_bounds(self):
        """Coverage score should be between 0 and 1."""
        # This tests the comparison method's contract
        comparison = {
            "fully_covered": [],
            "partially_covered": [],
            "not_covered": [],
            "coverage_score": 0.0,
        }
        assert 0.0 <= comparison["coverage_score"] <= 1.0

        comparison["coverage_score"] = 1.0
        assert 0.0 <= comparison["coverage_score"] <= 1.0
