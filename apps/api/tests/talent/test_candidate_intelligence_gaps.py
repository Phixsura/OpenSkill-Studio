"""Tests for gaps #131-145: Candidate Intelligence."""

from app.talent.services.candidate_intelligence import (
    ACHIEVEMENT_TYPES,
    AVAILABILITY_MODES,
    CURRENCY_CODES,
    MENTORSHIP_GOALS,
    MENTORSHIP_STATUSES,
    check_achievements,
    compute_mentorship_compatibility,
    compute_total_points,
    get_interview_prep,
    validate_availability_preference,
    validate_job_alert,
    validate_salary_expectation,
    validate_theme_preference,
)


class TestAvailability:
    def test_valid(self):
        pref = {
            "mode": "available_immediately",
            "hours_per_week": 40,
            "remote_preference": "flexible",
        }
        assert validate_availability_preference(pref) == []

    def test_invalid_mode(self):
        errors = validate_availability_preference({"mode": "invalid"})
        assert len(errors) > 0

    def test_invalid_hours(self):
        errors = validate_availability_preference({"hours_per_week": 100})
        assert len(errors) > 0

    def test_modes(self):
        assert "available_immediately" in AVAILABILITY_MODES
        assert len(AVAILABILITY_MODES) >= 5


class TestJobAlerts:
    def test_valid(self):
        assert validate_job_alert({"frequency": "daily", "min_match_score": 0.7}) == []

    def test_invalid_frequency(self):
        errors = validate_job_alert({"frequency": "hourly"})
        assert len(errors) > 0

    def test_invalid_score(self):
        errors = validate_job_alert({"min_match_score": 2.0})
        assert len(errors) > 0


class TestSalaryExpectation:
    def test_valid(self):
        exp = {"min_amount": 50000, "max_amount": 70000, "currency": "USD", "pay_period": "annual"}
        assert validate_salary_expectation(exp) == []

    def test_invalid_currency(self):
        errors = validate_salary_expectation({"currency": "XYZ"})
        assert len(errors) > 0

    def test_min_exceeds_max(self):
        errors = validate_salary_expectation({"min_amount": 100000, "max_amount": 50000})
        assert len(errors) > 0

    def test_currencies(self):
        assert "USD" in CURRENCY_CODES
        assert "CNY" in CURRENCY_CODES
        assert len(CURRENCY_CODES) >= 7


class TestMentorship:
    def test_compatibility_high(self):
        mentor = {
            "user_id": "m1",
            "capability_ids": ["c1", "c2", "c3"],
            "goals": ["skill_development"],
            "preferred_format": "video",
        }
        mentee = {
            "user_id": "e1",
            "capability_ids": ["c1", "c2"],
            "goals": ["skill_development"],
            "preferred_format": "video",
        }
        match = compute_mentorship_compatibility(mentor, mentee)
        assert match.compatibility_score > 0.7
        assert len(match.shared_capabilities) == 2

    def test_compatibility_low(self):
        mentor = {
            "user_id": "m1",
            "capability_ids": ["c1"],
            "goals": ["leadership"],
            "preferred_format": "in_person",
        }
        mentee = {
            "user_id": "e1",
            "capability_ids": ["c5", "c6"],
            "goals": ["career_guidance"],
            "preferred_format": "chat",
        }
        match = compute_mentorship_compatibility(mentor, mentee)
        assert match.compatibility_score < 0.4

    def test_statuses(self):
        assert "matched" in MENTORSHIP_STATUSES
        assert len(MENTORSHIP_GOALS) >= 6


class TestInterviewPrep:
    def test_technical(self):
        tips = get_interview_prep("technical")
        assert len(tips["specific_tips"]) > 0
        assert len(tips["general_tips"]) > 0

    def test_unknown_stage(self):
        tips = get_interview_prep("unknown")
        assert tips["stage_type"] == "unknown"
        assert len(tips["general_tips"]) > 0


class TestGamification:
    def test_earned_achievements(self):
        stats = {
            "evidence_count": 5,
            "capability_count": 6,
            "credential_count": 1,
            "endorsement_count": 2,
            "application_count": 3,
        }
        earned = check_achievements(stats)
        assert any(a["key"] == "first_evidence" for a in earned)
        assert any(a["key"] == "five_capabilities" for a in earned)
        assert any(a["key"] == "first_credential" for a in earned)

    def test_no_achievements(self):
        earned = check_achievements({})
        assert len(earned) == 0

    def test_points(self):
        earned = [ACHIEVEMENT_TYPES["first_evidence"], ACHIEVEMENT_TYPES["first_credential"]]
        points = compute_total_points(earned)
        assert points == 60  # 10 + 50

    def test_achievement_count(self):
        assert len(ACHIEVEMENT_TYPES) >= 9


class TestTheme:
    def test_valid(self):
        assert validate_theme_preference("dark") is True
        assert validate_theme_preference("light") is True
        assert validate_theme_preference("system") is True

    def test_invalid(self):
        assert validate_theme_preference("auto") is False
