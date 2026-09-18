"""Succession planning tests — pure logic, no DB needed."""

from app.talent.services.succession_planning import (
    READINESS_LEVELS,
    SuccessionPlanningService,
    SuccessorCandidate,
)

svc = SuccessionPlanningService()


class TestReadiness:
    def test_ready_now(self):
        r = svc.assess_readiness(capability_match=0.95, years_experience=5, has_leadership_evidence=True)
        assert r == "ready_now"

    def test_ready_1_year(self):
        r = svc.assess_readiness(capability_match=0.8, years_experience=3, has_leadership_evidence=False)
        assert r == "ready_1_year"

    def test_ready_2_years(self):
        r = svc.assess_readiness(capability_match=0.6, years_experience=1, has_leadership_evidence=False)
        assert r == "ready_2_years"

    def test_ready_3_plus(self):
        r = svc.assess_readiness(capability_match=0.35, years_experience=0.5, has_leadership_evidence=False)
        assert r == "ready_3_plus"

    def test_not_ready(self):
        r = svc.assess_readiness(capability_match=0.1, years_experience=0, has_leadership_evidence=False)
        assert r == "not_ready"


class TestCapabilityMatch:
    def test_full_match(self):
        levels = {"c1": 4, "c2": 3}
        required = [{"capability_id": "c1", "min_level": 3}, {"capability_id": "c2", "min_level": 2}]
        assert svc.compute_capability_match(levels, required) == 1.0

    def test_partial_match(self):
        levels = {"c1": 4}
        required = [{"capability_id": "c1", "min_level": 3}, {"capability_id": "c2", "min_level": 2}]
        assert svc.compute_capability_match(levels, required) == 0.5

    def test_no_match(self):
        levels = {}
        required = [{"capability_id": "c1", "min_level": 3}]
        assert svc.compute_capability_match(levels, required) == 0.0

    def test_empty_requirements(self):
        assert svc.compute_capability_match({}, []) == 1.0


class TestIdentifyGaps:
    def test_finds_gaps(self):
        levels = {"c1": 2}
        required = [
            {"capability_id": "c1", "capability_name": "AI", "min_level": 4},
            {"capability_id": "c2", "capability_name": "ML", "min_level": 3},
        ]
        gaps = svc.identify_gaps(levels, required)
        assert len(gaps) == 2
        assert gaps[0]["gap"] == 2
        assert gaps[1]["gap"] == 3

    def test_no_gaps(self):
        levels = {"c1": 5}
        required = [{"capability_id": "c1", "capability_name": "AI", "min_level": 3}]
        gaps = svc.identify_gaps(levels, required)
        assert len(gaps) == 0


class TestDevelopmentActions:
    def test_generates_actions(self):
        gaps = [
            {"capability_name": "AI", "gap": 1},
            {"capability_name": "ML", "gap": 2},
            {"capability_name": "DL", "gap": 3},
        ]
        actions = svc.generate_development_actions(gaps)
        assert len(actions) == 3
        assert "mentor" in actions[0].lower() or "experience" in actions[0].lower()
        assert "training" in actions[1].lower()


class TestRiskAssessment:
    def test_critical_risk(self):
        risk = svc.assess_risk(
            role_id="r1", role_title="CTO", criticality="critical",
            candidates=[],
        )
        assert risk.risk_level == "critical"
        assert "URGENT" in risk.recommendation

    def test_high_risk(self):
        candidates = [
            SuccessorCandidate("u1", "ready_2_years", 0.4, 0.6, [], [], 24),
        ]
        risk = svc.assess_risk(
            role_id="r1", role_title="VP Eng", criticality="high",
            candidates=candidates,
        )
        assert risk.risk_level == "high"

    def test_low_risk(self):
        candidates = [
            SuccessorCandidate("u1", "ready_now", 1.0, 0.95, [], [], None),
            SuccessorCandidate("u2", "ready_now", 1.0, 0.9, [], [], None),
        ]
        risk = svc.assess_risk(
            role_id="r1", role_title="Lead", criticality="medium",
            candidates=candidates,
        )
        assert risk.risk_level == "low"


class TestConstants:
    def test_readiness_levels(self):
        assert len(READINESS_LEVELS) == 5
        assert READINESS_LEVELS["ready_now"]["score"] == 1.0
        assert READINESS_LEVELS["not_ready"]["score"] == 0.0
