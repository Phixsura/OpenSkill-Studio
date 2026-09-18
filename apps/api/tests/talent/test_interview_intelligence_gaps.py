"""Tests for gaps #51-65, #96-105: Assessment & Interview Intelligence."""

from datetime import UTC, datetime, timedelta

from app.talent.services.interview_intelligence import (
    DAYS_OF_WEEK,
    NO_SHOW_STATUSES,
    QUESTION_CATEGORIES,
    check_renewal_eligibility,
    classify_attendance,
    compute_assessment_difficulty,
    compute_debrief_summary,
    compute_reminder_schedule,
    compute_score_distribution,
    generate_booking_link,
    get_rubric_template,
    list_rubric_templates,
    validate_availability,
    validate_question_bank_item,
)


class TestQuestionBank:
    def test_valid_item(self):
        item = {
            "question_text": "Explain polymorphism in OOP",
            "category": "knowledge",
            "difficulty": "medium",
        }
        assert validate_question_bank_item(item) == []

    def test_short_text(self):
        errors = validate_question_bank_item({"question_text": "Short"})
        assert len(errors) > 0

    def test_invalid_category(self):
        errors = validate_question_bank_item(
            {"question_text": "Valid question text here", "category": "invalid"}
        )
        assert any("category" in e.lower() for e in errors)

    def test_categories(self):
        assert "knowledge" in QUESTION_CATEGORIES
        assert "technical" in QUESTION_CATEGORIES
        assert len(QUESTION_CATEGORIES) == 5


class TestRubricTemplates:
    def test_list(self):
        templates = list_rubric_templates()
        assert "technical_interview" in templates
        assert "portfolio_review" in templates

    def test_get(self):
        t = get_rubric_template("technical_interview")
        assert t is not None
        assert len(t["criteria"]) >= 3

    def test_unknown(self):
        assert get_rubric_template("nonexistent") is None


class TestAssessmentAnalytics:
    def test_difficulty_easy(self):
        assert compute_assessment_difficulty(0.90) == "easy"

    def test_difficulty_medium(self):
        assert compute_assessment_difficulty(0.60) == "medium"

    def test_difficulty_hard(self):
        assert compute_assessment_difficulty(0.30) == "hard"

    def test_score_distribution(self):
        scores = [0.1, 0.3, 0.5, 0.7, 0.9]
        dist = compute_score_distribution(scores)
        assert sum(dist.values()) == 5
        assert dist["81-100"] == 1


class TestCredentialRenewal:
    def test_eligible(self):
        expires = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        result = check_renewal_eligibility({"expires_at": expires})
        assert result["eligible"] is True

    def test_not_eligible_too_early(self):
        expires = (datetime.now(UTC) + timedelta(days=200)).isoformat()
        result = check_renewal_eligibility({"expires_at": expires})
        assert result["eligible"] is False

    def test_expired(self):
        expires = (datetime.now(UTC) - timedelta(days=10)).isoformat()
        result = check_renewal_eligibility({"expires_at": expires})
        assert result["eligible"] is True
        assert result["status"] == "expired"

    def test_no_expiration(self):
        result = check_renewal_eligibility({})
        assert result["eligible"] is False


class TestAvailability:
    def test_valid(self):
        slots = [{"day": "monday", "start_hour": 9, "end_hour": 17}]
        assert validate_availability(slots) == []

    def test_invalid_day(self):
        errors = validate_availability([{"day": "funday", "start_hour": 9, "end_hour": 17}])
        assert len(errors) > 0

    def test_invalid_hours(self):
        errors = validate_availability([{"day": "monday", "start_hour": 17, "end_hour": 9}])
        assert len(errors) > 0

    def test_days(self):
        assert len(DAYS_OF_WEEK) == 7


class TestBookingLink:
    def test_generates(self):
        link = generate_booking_link("stage123")
        assert "/book/" in link["url"]
        assert link["interview_stage_id"] == "stage123"
        assert len(link["token"]) == 16


class TestReminders:
    def test_future_interview(self):
        future = datetime.now(UTC) + timedelta(hours=48)
        reminders = compute_reminder_schedule(future)
        assert len(reminders) == 3  # 24h, 1h, 15m

    def test_soon_interview(self):
        soon = datetime.now(UTC) + timedelta(minutes=10)
        reminders = compute_reminder_schedule(soon)
        assert len(reminders) == 0  # all past


class TestNoShow:
    def test_attended(self):
        scheduled = datetime.now(UTC) - timedelta(hours=1)
        joined = scheduled + timedelta(minutes=2)
        assert classify_attendance(scheduled, joined) == "attended"

    def test_late(self):
        scheduled = datetime.now(UTC) - timedelta(hours=1)
        joined = scheduled + timedelta(minutes=20)
        assert classify_attendance(scheduled, joined) == "late"

    def test_no_show(self):
        scheduled = datetime.now(UTC) - timedelta(hours=2)
        assert classify_attendance(scheduled, None) == "no_show_candidate"

    def test_statuses(self):
        assert "no_show_candidate" in NO_SHOW_STATUSES
        assert "no_show_interviewer" in NO_SHOW_STATUSES


class TestDebrief:
    def test_unanimous_hire(self):
        cards = [
            {"interview_stage_id": "s1", "overall_rating": 4, "recommendation": "hire"},
            {"interview_stage_id": "s1", "overall_rating": 5, "recommendation": "hire"},
        ]
        result = compute_debrief_summary(cards)
        assert result.consensus == "unanimous_hire"
        assert result.avg_overall_rating == 4.5

    def test_mixed(self):
        cards = [
            {"interview_stage_id": "s1", "overall_rating": 5, "recommendation": "strong_hire"},
            {"interview_stage_id": "s1", "overall_rating": 2, "recommendation": "no_hire"},
        ]
        result = compute_debrief_summary(cards)
        assert result.consensus == "mixed"

    def test_empty(self):
        result = compute_debrief_summary([])
        assert result.consensus == "insufficient"
