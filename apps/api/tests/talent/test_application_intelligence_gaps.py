"""Tests for gaps #81-95: Application Pipeline Intelligence."""

from datetime import UTC, datetime, timedelta

from app.talent.services.application_intelligence import (
    DEFAULT_STAGE_LIMITS_DAYS,
    QUESTION_TYPES,
    SCREENING_RULE_TYPES,
    WITHDRAWAL_REASONS,
    build_application_timeline,
    check_stage_overdue,
    evaluate_screening_rules,
    validate_batch_action,
    validate_custom_questions,
    validate_reference,
    validate_withdrawal_reason,
)


class TestFormBuilder:
    def test_valid_questions(self):
        qs = [{"question_text": "Why?", "question_type": "textarea"}]
        assert validate_custom_questions(qs) == []

    def test_invalid_type(self):
        qs = [{"question_text": "Q", "question_type": "invalid"}]
        errors = validate_custom_questions(qs)
        assert any("type" in e.lower() for e in errors)

    def test_select_needs_options(self):
        qs = [{"question_text": "Pick", "question_type": "select"}]
        errors = validate_custom_questions(qs)
        assert any("options" in e.lower() for e in errors)

    def test_max_questions(self):
        qs = [{"question_text": f"Q{i}", "question_type": "text"} for i in range(25)]
        errors = validate_custom_questions(qs)
        assert any("20" in e for e in errors)

    def test_question_types(self):
        assert "text" in QUESTION_TYPES
        assert "file_upload" in QUESTION_TYPES
        assert len(QUESTION_TYPES) >= 8


class TestAutoScreening:
    def test_all_pass(self):
        rules = [
            {"rule_type": "min_capability_level", "field": "level", "operator": ">=", "value": 3}
        ]
        result = evaluate_screening_rules(rules, {"level": 4})
        assert result["passed"] is True
        assert result["score"] == 1.0

    def test_fail(self):
        rules = [
            {"rule_type": "min_capability_level", "field": "level", "operator": ">=", "value": 5}
        ]
        result = evaluate_screening_rules(rules, {"level": 2})
        assert result["passed"] is False

    def test_empty_rules(self):
        result = evaluate_screening_rules([], {})
        assert result["passed"] is True

    def test_rule_types(self):
        assert "keyword_match" in SCREENING_RULE_TYPES
        assert len(SCREENING_RULE_TYPES) >= 5


class TestWithdrawalReasons:
    def test_valid(self):
        assert validate_withdrawal_reason("accepted_other_offer") is True

    def test_invalid(self):
        assert validate_withdrawal_reason("invalid") is False

    def test_all_reasons(self):
        assert len(WITHDRAWAL_REASONS) >= 8


class TestTimeline:
    def test_builds_timeline(self):
        events = [
            {"to_status": "submitted", "timestamp": "2026-01-01T10:00:00", "acted_by": "u1"},
            {"to_status": "screening", "timestamp": "2026-01-03T14:00:00", "acted_by": "e1"},
        ]
        timeline = build_application_timeline(events)
        assert len(timeline) == 2
        assert timeline[0].stage == "submitted"
        assert timeline[1].duration_from_previous_hours is not None

    def test_empty(self):
        assert build_application_timeline([]) == []


class TestBatchActions:
    def test_valid(self):
        errors = validate_batch_action("reject", ["a1", "a2"])
        assert errors == []

    def test_invalid_action(self):
        errors = validate_batch_action("invalid", ["a1"])
        assert len(errors) > 0

    def test_too_many(self):
        errors = validate_batch_action("reject", [f"a{i}" for i in range(60)])
        assert any("50" in e for e in errors)

    def test_duplicates(self):
        errors = validate_batch_action("reject", ["a1", "a1"])
        assert any("duplicate" in e.lower() for e in errors)

    def test_empty_ids(self):
        errors = validate_batch_action("reject", [])
        assert len(errors) > 0


class TestReferenceChecks:
    def test_valid(self):
        ref = {
            "referee_name": "John",
            "referee_email": "j@test.com",
            "referee_relationship": "Manager",
        }
        assert validate_reference(ref) == []

    def test_missing_email(self):
        ref = {"referee_name": "John", "referee_email": "", "referee_relationship": "Manager"}
        errors = validate_reference(ref)
        assert any("email" in e.lower() for e in errors)


class TestStageTimeLimits:
    def test_not_overdue(self):
        result = check_stage_overdue("screening", datetime.now(UTC) - timedelta(days=3))
        assert result["overdue"] is False
        assert result["days_remaining"] > 0

    def test_overdue(self):
        result = check_stage_overdue("screening", datetime.now(UTC) - timedelta(days=10))
        assert result["overdue"] is True

    def test_no_limit(self):
        result = check_stage_overdue("submitted", datetime.now(UTC))
        assert result["overdue"] is False
        assert result["limit_days"] is None

    def test_defaults(self):
        assert "screening" in DEFAULT_STAGE_LIMITS_DAYS
        assert "interview" in DEFAULT_STAGE_LIMITS_DAYS
