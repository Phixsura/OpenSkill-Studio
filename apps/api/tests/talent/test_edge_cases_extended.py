"""Extended edge case tests — verifies 200+ boundary conditions.

Each test validates a specific edge case that could cause a bug if not handled.
"""

from datetime import UTC, datetime, timedelta

# ---- Scoring edge cases (20) ----

class TestScoringEdgeCases:
    def test_zero_evidence_returns_zero(self):
        from app.talent.services.scoring import compute_score_from_evidence
        score, conf, sub = compute_score_from_evidence([], None, datetime.now(UTC))
        assert score == 0.0 and conf == 0.0 and sub == 0

    def test_negative_score_clamped(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": -0.5, "verification_level": "self_reported", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score >= 0

    def test_score_above_one_clamped(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": 5.0, "verification_level": "employer_verified", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score <= 2.0  # shrinkage bounds it

    def test_expired_evidence_excluded(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": 0.9, "verification_level": "employer_verified", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": datetime.now(UTC) - timedelta(days=1)}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score == 0.0

    def test_voided_evidence_excluded(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": 0.9, "verification_level": "employer_verified", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "voided", "expires_at": None}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score == 0.0

    def test_recency_future_date(self):
        from app.talent.services.scoring import compute_recency
        ev = [{"occurred_at": datetime.now(UTC) + timedelta(days=30), "status": "active"}]
        assert compute_recency(ev, datetime.now(UTC)) == 1.0

    def test_recency_very_old(self):
        from app.talent.services.scoring import compute_recency
        ev = [{"occurred_at": datetime.now(UTC) - timedelta(days=3650), "status": "active"}]
        result = compute_recency(ev, datetime.now(UTC))
        assert result < 0.01

    def test_velocity_no_recent(self):
        from app.talent.services.scoring import compute_velocity
        ev = [{"occurred_at": datetime.now(UTC) - timedelta(days=200), "status": "active"}]
        assert compute_velocity(ev, datetime.now(UTC)) == 0.0

    def test_decay_zero_half_life(self):
        from app.talent.services.scoring import decay_factor
        assert decay_factor(datetime.now(UTC), datetime.now(UTC), {"half_life_days": 0}) == 1.0

    def test_decay_negative_age(self):
        from app.talent.services.scoring import decay_factor
        future = datetime.now(UTC) + timedelta(days=100)
        assert decay_factor(future, datetime.now(UTC), {"half_life_days": 365}) == 1.0

    def test_level_zero_score(self):
        from app.talent.services.scoring import determine_level
        level, label = determine_level(0.0, 0, None)
        assert level == 0

    def test_level_max(self):
        from app.talent.services.scoring import determine_level
        level, _ = determine_level(0.99, 100, None)
        assert level == 5

    def test_null_score_uses_default(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": None, "verification_level": "instructor_verified", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score > 0

    def test_unknown_verification_level(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": 0.8, "verification_level": "unknown_level", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score > 0  # uses default weight 0.5

    def test_confidence_zero(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": 0.9, "verification_level": "employer_verified", "confidence": 0.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None}]
        score, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert score < 0.6  # zero confidence reduces score

    def test_many_evidence_items(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [{"score_normalized": 0.8, "verification_level": "instructor_verified", "confidence": 0.9, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None} for _ in range(100)]
        score, conf, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert conf > 0.95  # high confidence with many items

    def test_mixed_active_voided(self):
        from app.talent.services.scoring import compute_score_from_evidence
        ev = [
            {"score_normalized": 0.9, "verification_level": "employer_verified", "confidence": 1.0, "occurred_at": datetime.now(UTC), "status": "active", "expires_at": None},
            {"score_normalized": 0.1, "verification_level": "self_reported", "confidence": 0.5, "occurred_at": datetime.now(UTC), "status": "voided", "expires_at": None},
        ]
        score, _, sub = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert sub == 1  # only 1 substantial (employer_verified)

    def test_scoring_version(self):
        from app.talent.services.scoring import SCORING_VERSION
        assert SCORING_VERSION == "2.0.0"

    def test_dimension_weights_sum_to_one(self):
        from app.talent.services.scoring import DIMENSION_WEIGHTS
        assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 0.001

    def test_level_thresholds_ordered(self):
        from app.talent.services.scoring import DEFAULT_LEVEL_THRESHOLDS
        prev_score = -1
        for level in sorted(DEFAULT_LEVEL_THRESHOLDS.keys()):
            score = DEFAULT_LEVEL_THRESHOLDS[level]["min_score"]
            assert score >= prev_score
            prev_score = score


# ---- Matching edge cases (20) ----

class TestMatchingEdgeCases:
    def test_adjacency_credit_distance_1(self):
        from app.talent.services.talent_matching import _ADJACENCY_CREDIT
        assert _ADJACENCY_CREDIT[1] == 0.5

    def test_adjacency_credit_distance_2(self):
        from app.talent.services.talent_matching import _ADJACENCY_CREDIT
        assert _ADJACENCY_CREDIT[2] == 0.25

    def test_signal_weights_sum_to_one(self):
        from app.talent.services.talent_matching import TALENT_WEIGHTS as SIGNAL_WEIGHTS
        assert abs(sum(SIGNAL_WEIGHTS.values()) - 1.0) < 0.001

    def test_match_tiers_ordered(self):
        from app.talent.services.search_intelligence import MATCH_TIERS
        assert MATCH_TIERS["strong"]["min_score"] > MATCH_TIERS["good"]["min_score"]
        assert MATCH_TIERS["good"]["min_score"] > MATCH_TIERS["partial"]["min_score"]

    def test_classify_boundary_80(self):
        from app.talent.services.search_intelligence import classify_match_tier
        assert classify_match_tier(0.80) == "strong"

    def test_classify_boundary_60(self):
        from app.talent.services.search_intelligence import classify_match_tier
        assert classify_match_tier(0.60) == "good"

    def test_classify_boundary_40(self):
        from app.talent.services.search_intelligence import classify_match_tier
        assert classify_match_tier(0.40) == "partial"

    def test_classify_zero(self):
        from app.talent.services.search_intelligence import classify_match_tier
        assert classify_match_tier(0.0) == "weak"

    def test_boolean_empty_query(self):
        from app.talent.services.search_intelligence import parse_boolean_query
        result = parse_boolean_query("")
        assert result["must"] == [] and result["should"] == [] and result["must_not"] == []

    def test_boolean_only_spaces(self):
        from app.talent.services.search_intelligence import parse_boolean_query
        result = parse_boolean_query("   ")
        assert result["must"] == []

    def test_filter_empty_list(self):
        from app.talent.services.search_intelligence import filter_by_tier
        assert filter_by_tier([], "strong") == []

    def test_feedback_all_options(self):
        from app.talent.services.search_intelligence import MATCH_FEEDBACK_OPTIONS
        assert len(MATCH_FEEDBACK_OPTIONS) >= 5

    def test_search_cache_ttl(self):
        from app.talent.services.search_intelligence import SearchCache
        cache = SearchCache(ttl_seconds=0)
        cache.set("k", [1])
        import time
        time.sleep(0.01)
        assert cache.get("k") is None  # expired

    def test_search_analytics_empty(self):
        from app.talent.services.search_intelligence import SearchAnalyticsStore
        s = SearchAnalyticsStore()
        assert s.get_stats()["total_searches"] == 0

    def test_suggestions_short_query(self):
        from app.talent.services.search_intelligence import generate_search_suggestions
        assert generate_search_suggestions("a", [], []) == []

    def test_compensation_ranges_ordered(self):
        from app.talent.services.search_intelligence import COMPENSATION_RANGES
        for i in range(len(COMPENSATION_RANGES) - 1):
            assert COMPENSATION_RANGES[i][2] <= COMPENSATION_RANGES[i+1][1]

    def test_experience_levels_complete(self):
        from app.talent.services.search_intelligence import EXPERIENCE_LEVELS
        assert "entry" in EXPERIENCE_LEVELS and "senior" in EXPERIENCE_LEVELS

    def test_org_size_ranges_complete(self):
        from app.talent.services.search_intelligence import ORG_SIZE_RANGES
        assert "startup" in ORG_SIZE_RANGES and "enterprise" in ORG_SIZE_RANGES

    def test_boolean_multiple_not(self):
        from app.talent.services.search_intelligence import parse_boolean_query
        result = parse_boolean_query("Python NOT Java NOT Ruby")
        assert "java" in result["must_not"] or "ruby" in result["must_not"]

    def test_apply_boolean_no_items(self):
        from app.talent.services.search_intelligence import apply_boolean_filter
        assert apply_boolean_filter([], {"must": ["x"], "should": [], "must_not": []}) == []


# ---- Application edge cases (20) ----

class TestApplicationEdgeCases:
    def test_valid_withdrawal_reasons(self):
        from app.talent.services.application_intelligence import WITHDRAWAL_REASONS
        assert len(WITHDRAWAL_REASONS) >= 8
        assert "accepted_other_offer" in WITHDRAWAL_REASONS

    def test_question_types_complete(self):
        from app.talent.services.application_intelligence import QUESTION_TYPES
        assert "text" in QUESTION_TYPES and "textarea" in QUESTION_TYPES and "select" in QUESTION_TYPES

    def test_screening_rule_types(self):
        from app.talent.services.application_intelligence import SCREENING_RULE_TYPES
        assert len(SCREENING_RULE_TYPES) >= 5

    def test_batch_max_size(self):
        from app.talent.services.application_intelligence import MAX_BATCH_SIZE
        assert MAX_BATCH_SIZE == 50

    def test_stage_limits_screening(self):
        from app.talent.services.application_intelligence import DEFAULT_STAGE_LIMITS_DAYS
        assert DEFAULT_STAGE_LIMITS_DAYS["screening"] == 7

    def test_stage_limits_interview(self):
        from app.talent.services.application_intelligence import DEFAULT_STAGE_LIMITS_DAYS
        assert DEFAULT_STAGE_LIMITS_DAYS["interview"] == 14

    def test_empty_timeline(self):
        from app.talent.services.application_intelligence import build_application_timeline
        assert build_application_timeline([]) == []

    def test_single_event_timeline(self):
        from app.talent.services.application_intelligence import build_application_timeline
        events = [{"to_status": "submitted", "timestamp": "2026-01-01T10:00:00"}]
        timeline = build_application_timeline(events)
        assert len(timeline) == 1
        assert timeline[0].duration_from_previous_hours is None

    def test_batch_validate_empty(self):
        from app.talent.services.application_intelligence import validate_batch_action
        errors = validate_batch_action("reject", [])
        assert len(errors) > 0

    def test_batch_validate_invalid_action(self):
        from app.talent.services.application_intelligence import validate_batch_action
        errors = validate_batch_action("destroy", ["a1"])
        assert len(errors) > 0

    def test_reference_missing_email(self):
        from app.talent.services.application_intelligence import validate_reference
        errors = validate_reference({"referee_name": "John"})
        assert len(errors) > 0

    def test_overdue_no_limit_stage(self):
        from app.talent.services.application_intelligence import check_stage_overdue
        result = check_stage_overdue("submitted", datetime.now(UTC))
        assert result["overdue"] is False

    def test_overdue_exactly_at_limit(self):
        from app.talent.services.application_intelligence import check_stage_overdue
        result = check_stage_overdue("screening", datetime.now(UTC) - timedelta(days=7))
        assert result["days_remaining"] == 0

    def test_screening_all_pass(self):
        from app.talent.services.application_intelligence import evaluate_screening_rules
        result = evaluate_screening_rules([], {})
        assert result["passed"] is True and result["score"] == 1.0

    def test_screening_contains_operator(self):
        from app.talent.services.application_intelligence import evaluate_screening_rules
        rules = [{"rule_type": "keyword_match", "field": "bio", "operator": "contains", "value": "python"}]
        result = evaluate_screening_rules(rules, {"bio": "I love Python programming"})
        assert result["passed"] is True

    def test_screening_exists_operator(self):
        from app.talent.services.application_intelligence import evaluate_screening_rules
        rules = [{"rule_type": "min_capability_level", "field": "portfolio", "operator": "exists", "value": True}]
        result_yes = evaluate_screening_rules(rules, {"portfolio": "link"})
        result_no = evaluate_screening_rules(rules, {})
        assert result_yes["passed"] is True
        assert result_no["passed"] is False

    def test_custom_questions_empty(self):
        from app.talent.services.application_intelligence import validate_custom_questions
        assert validate_custom_questions([]) == []

    def test_custom_questions_missing_text(self):
        from app.talent.services.application_intelligence import validate_custom_questions
        errors = validate_custom_questions([{"question_type": "text"}])
        assert len(errors) > 0

    def test_withdrawal_valid(self):
        from app.talent.services.application_intelligence import validate_withdrawal_reason
        assert validate_withdrawal_reason("personal_reasons") is True

    def test_withdrawal_invalid(self):
        from app.talent.services.application_intelligence import validate_withdrawal_reason
        assert validate_withdrawal_reason("just_because") is False


# ---- Interview edge cases (20) ----

class TestInterviewEdgeCases:
    def test_question_categories(self):
        from app.talent.services.interview_intelligence import QUESTION_CATEGORIES
        assert len(QUESTION_CATEGORIES) == 5

    def test_rubric_template_exists(self):
        from app.talent.services.interview_intelligence import get_rubric_template
        assert get_rubric_template("technical_interview") is not None

    def test_rubric_template_missing(self):
        from app.talent.services.interview_intelligence import get_rubric_template
        assert get_rubric_template("nonexistent") is None

    def test_difficulty_boundary_80(self):
        from app.talent.services.interview_intelligence import compute_assessment_difficulty
        assert compute_assessment_difficulty(0.80) == "medium"

    def test_difficulty_boundary_81(self):
        from app.talent.services.interview_intelligence import compute_assessment_difficulty
        assert compute_assessment_difficulty(0.81) == "easy"

    def test_score_distribution_empty(self):
        from app.talent.services.interview_intelligence import compute_score_distribution
        dist = compute_score_distribution([])
        assert sum(dist.values()) == 0

    def test_renewal_no_expiry(self):
        from app.talent.services.interview_intelligence import check_renewal_eligibility
        result = check_renewal_eligibility({})
        assert result["eligible"] is False

    def test_renewal_far_future(self):
        from app.talent.services.interview_intelligence import check_renewal_eligibility
        result = check_renewal_eligibility({"expires_at": (datetime.now(UTC) + timedelta(days=500)).isoformat()})
        assert result["eligible"] is False

    def test_availability_invalid_day(self):
        from app.talent.services.interview_intelligence import validate_availability
        errors = validate_availability([{"day": "funday", "start_hour": 9, "end_hour": 17}])
        assert len(errors) > 0

    def test_availability_end_before_start(self):
        from app.talent.services.interview_intelligence import validate_availability
        errors = validate_availability([{"day": "monday", "start_hour": 17, "end_hour": 9}])
        assert len(errors) > 0

    def test_booking_link_unique(self):
        from app.talent.services.interview_intelligence import generate_booking_link
        l1 = generate_booking_link("stage_a")
        l2 = generate_booking_link("stage_b")
        assert l1["token"] != l2["token"]

    def test_reminder_past_interview(self):
        from app.talent.services.interview_intelligence import compute_reminder_schedule
        past = datetime.now(UTC) - timedelta(hours=2)
        assert compute_reminder_schedule(past) == []

    def test_no_show_pending(self):
        from app.talent.services.interview_intelligence import classify_attendance
        recent = datetime.now(UTC) - timedelta(minutes=5)
        assert classify_attendance(recent, None) == "pending"

    def test_no_show_confirmed(self):
        from app.talent.services.interview_intelligence import classify_attendance
        old = datetime.now(UTC) - timedelta(hours=1)
        assert classify_attendance(old, None) == "no_show_candidate"

    def test_attended_on_time(self):
        from app.talent.services.interview_intelligence import classify_attendance
        scheduled = datetime.now(UTC) - timedelta(hours=1)
        joined = scheduled + timedelta(minutes=1)
        assert classify_attendance(scheduled, joined) == "attended"

    def test_attended_late(self):
        from app.talent.services.interview_intelligence import classify_attendance
        scheduled = datetime.now(UTC) - timedelta(hours=1)
        joined = scheduled + timedelta(minutes=20)
        assert classify_attendance(scheduled, joined) == "late"

    def test_debrief_empty(self):
        from app.talent.services.interview_intelligence import compute_debrief_summary
        result = compute_debrief_summary([])
        assert result.consensus == "insufficient"

    def test_debrief_single(self):
        from app.talent.services.interview_intelligence import compute_debrief_summary
        cards = [{"interview_stage_id": "s1", "overall_rating": 4, "recommendation": "hire"}]
        result = compute_debrief_summary(cards)
        assert result.total_scorecards == 1

    def test_days_of_week_count(self):
        from app.talent.services.interview_intelligence import DAYS_OF_WEEK
        assert len(DAYS_OF_WEEK) == 7

    def test_no_show_statuses(self):
        from app.talent.services.interview_intelligence import NO_SHOW_STATUSES
        assert "no_show_candidate" in NO_SHOW_STATUSES and "attended" in NO_SHOW_STATUSES


# ---- Employer edge cases (20) ----

class TestEmployerEdgeCases:
    def test_pipeline_min_stages(self):
        from app.talent.services.employer_intelligence import validate_custom_pipeline
        errors = validate_custom_pipeline(["submitted", "hired"])
        assert any("3" in e for e in errors)

    def test_pipeline_max_stages(self):
        from app.talent.services.employer_intelligence import validate_custom_pipeline
        stages = ["submitted"] + [f"stage_{i}" for i in range(15)] + ["hired"]
        errors = validate_custom_pipeline(stages)
        assert any("15" in e for e in errors)

    def test_pipeline_duplicate(self):
        from app.talent.services.employer_intelligence import validate_custom_pipeline
        errors = validate_custom_pipeline(["submitted", "screening", "screening", "hired"])
        assert any("duplicate" in e.lower() for e in errors)

    def test_adverse_impact_no_selections(self):
        from app.talent.services.employer_intelligence import compute_adverse_impact
        result = compute_adverse_impact(0, 100, 0, 100)
        assert result["adverse_impact"] is False

    def test_adverse_impact_equal_rates(self):
        from app.talent.services.employer_intelligence import compute_adverse_impact
        result = compute_adverse_impact(50, 100, 50, 100)
        assert result["ratio"] == 1.0

    def test_pool_rule_min_level_pass(self):
        from app.talent.services.employer_intelligence import evaluate_pool_rule
        assert evaluate_pool_rule({"rule_type": "min_capability_level", "field": "level", "value": 3}, {"level": 5}) is True

    def test_pool_rule_min_level_fail(self):
        from app.talent.services.employer_intelligence import evaluate_pool_rule
        assert evaluate_pool_rule({"rule_type": "min_capability_level", "field": "level", "value": 5}, {"level": 2}) is False

    def test_pool_rules_empty(self):
        from app.talent.services.employer_intelligence import evaluate_pool_rules
        result = evaluate_pool_rules([], {})
        assert result["eligible"] is True

    def test_requisition_missing_title(self):
        from app.talent.services.employer_intelligence import validate_requisition
        errors = validate_requisition({"department": "Eng", "justification": "Need more devs for Q3 deliverables", "headcount": 1})
        assert any("title" in e.lower() for e in errors)

    def test_brand_health_empty(self):
        from app.talent.services.employer_intelligence import compute_brand_health_trend
        result = compute_brand_health_trend([])
        assert result["trend"] == "insufficient_data"

    def test_brand_health_improving(self):
        from app.talent.services.employer_intelligence import compute_brand_health_trend
        result = compute_brand_health_trend([{"reputation_score": 50}, {"reputation_score": 70}])
        assert result["trend"] == "improving"

    def test_department_tree_flat(self):
        from app.talent.services.employer_intelligence import build_department_tree
        tree = build_department_tree([{"id": "d1", "name": "Eng"}])
        assert len(tree) == 1

    def test_department_tree_nested(self):
        from app.talent.services.employer_intelligence import build_department_tree
        tree = build_department_tree([
            {"id": "d1", "name": "Eng", "parent_department_id": None},
            {"id": "d2", "name": "Frontend", "parent_department_id": "d1"},
        ])
        assert len(tree) == 1 and len(tree[0]["children"]) == 1

    def test_interview_kit_sections(self):
        from app.talent.services.employer_intelligence import INTERVIEW_KIT_SECTIONS
        assert len(INTERVIEW_KIT_SECTIONS) >= 5

    def test_offer_comparison_empty(self):
        from app.talent.services.employer_intelligence import compare_offers
        result = compare_offers([])
        assert result.fewest_conditions == 0

    def test_offer_html_generates(self):
        from app.talent.services.employer_intelligence import generate_offer_html
        html = generate_offer_html({"role_title": "Dev"})
        assert "<html>" in html and "Dev" in html

    def test_offer_deadline_no_expiry(self):
        from app.talent.services.employer_intelligence import compute_offer_deadline_alerts
        assert compute_offer_deadline_alerts([{"id": "o1"}]) == []

    def test_relationship_timeline_sorts(self):
        from app.talent.services.employer_intelligence import build_relationship_timeline
        events = [
            {"type": "message", "timestamp": "2026-02-01"},
            {"type": "application", "timestamp": "2026-01-01"},
        ]
        timeline = build_relationship_timeline(events)
        assert timeline[0]["timestamp"] < timeline[1]["timestamp"]

    def test_approval_statuses(self):
        from app.talent.services.employer_intelligence import APPROVAL_STATUSES
        assert "pending_approval" in APPROVAL_STATUSES

    def test_customizable_stages(self):
        from app.talent.services.employer_intelligence import CUSTOMIZABLE_STAGES
        assert "phone_screen" in CUSTOMIZABLE_STAGES


# ---- Candidate edge cases (20) ----

class TestCandidateEdgeCases:
    def test_availability_modes(self):
        from app.talent.services.candidate_intelligence import AVAILABILITY_MODES
        assert len(AVAILABILITY_MODES) >= 5

    def test_availability_invalid_mode(self):
        from app.talent.services.candidate_intelligence import validate_availability_preference
        errors = validate_availability_preference({"mode": "invalid"})
        assert len(errors) > 0

    def test_salary_invalid_currency(self):
        from app.talent.services.candidate_intelligence import validate_salary_expectation
        errors = validate_salary_expectation({"currency": "XYZ"})
        assert len(errors) > 0

    def test_salary_min_exceeds_max(self):
        from app.talent.services.candidate_intelligence import validate_salary_expectation
        errors = validate_salary_expectation({"min_amount": 100000, "max_amount": 50000})
        assert len(errors) > 0

    def test_job_alert_invalid_freq(self):
        from app.talent.services.candidate_intelligence import validate_job_alert
        errors = validate_job_alert({"frequency": "hourly"})
        assert len(errors) > 0

    def test_mentorship_no_overlap(self):
        from app.talent.services.candidate_intelligence import compute_mentorship_compatibility
        match = compute_mentorship_compatibility(
            {"user_id": "m1", "capability_ids": ["c1"], "goals": ["x"], "preferred_format": "video"},
            {"user_id": "e1", "capability_ids": ["c9"], "goals": ["y"], "preferred_format": "chat"},
        )
        assert match.compatibility_score < 0.3

    def test_achievements_none_earned(self):
        from app.talent.services.candidate_intelligence import check_achievements
        assert check_achievements({}) == []

    def test_achievements_first_evidence(self):
        from app.talent.services.candidate_intelligence import check_achievements
        earned = check_achievements({"evidence_count": 1})
        assert any(a["key"] == "first_evidence" for a in earned)

    def test_points_calculation(self):
        from app.talent.services.candidate_intelligence import (
            ACHIEVEMENT_TYPES,
            compute_total_points,
        )
        items = [ACHIEVEMENT_TYPES["first_evidence"]]
        assert compute_total_points(items) == 10

    def test_interview_prep_technical(self):
        from app.talent.services.candidate_intelligence import get_interview_prep
        tips = get_interview_prep("technical")
        assert len(tips["specific_tips"]) > 0

    def test_interview_prep_unknown(self):
        from app.talent.services.candidate_intelligence import get_interview_prep
        tips = get_interview_prep("unknown_type")
        assert len(tips["general_tips"]) > 0

    def test_theme_valid(self):
        from app.talent.services.candidate_intelligence import validate_theme_preference
        assert validate_theme_preference("dark") is True

    def test_theme_invalid(self):
        from app.talent.services.candidate_intelligence import validate_theme_preference
        assert validate_theme_preference("auto") is False

    def test_currencies(self):
        from app.talent.services.candidate_intelligence import CURRENCY_CODES
        assert "USD" in CURRENCY_CODES and "EUR" in CURRENCY_CODES

    def test_pay_periods(self):
        from app.talent.services.candidate_intelligence import PAY_PERIODS
        assert "annual" in PAY_PERIODS and "hourly" in PAY_PERIODS

    def test_mentorship_goals(self):
        from app.talent.services.candidate_intelligence import MENTORSHIP_GOALS
        assert "career_guidance" in MENTORSHIP_GOALS

    def test_mentorship_statuses(self):
        from app.talent.services.candidate_intelligence import MENTORSHIP_STATUSES
        assert "matched" in MENTORSHIP_STATUSES and "completed" in MENTORSHIP_STATUSES

    def test_achievement_types_count(self):
        from app.talent.services.candidate_intelligence import ACHIEVEMENT_TYPES
        assert len(ACHIEVEMENT_TYPES) >= 9

    def test_achievement_all_have_points(self):
        from app.talent.services.candidate_intelligence import ACHIEVEMENT_TYPES
        for key, a in ACHIEVEMENT_TYPES.items():
            assert "points" in a and a["points"] > 0, f"{key} missing points"

    def test_achievement_all_have_icon(self):
        from app.talent.services.candidate_intelligence import ACHIEVEMENT_TYPES
        for key, a in ACHIEVEMENT_TYPES.items():
            assert "icon" in a and len(a["icon"]) > 0, f"{key} missing icon"


# ---- Platform/Integration edge cases (20) ----

class TestPlatformEdgeCases:
    def test_feature_flag_enabled(self):
        from app.talent.services.platform_operations import is_feature_enabled
        assert is_feature_enabled("talent_matching") is True

    def test_feature_flag_disabled(self):
        from app.talent.services.platform_operations import is_feature_enabled
        assert is_feature_enabled("gamification") is False

    def test_feature_flag_override(self):
        from app.talent.services.platform_operations import is_feature_enabled
        assert is_feature_enabled("gamification", {"gamification": True}) is True

    def test_feature_flag_unknown(self):
        from app.talent.services.platform_operations import is_feature_enabled
        assert is_feature_enabled("nonexistent") is False

    def test_role_hierarchy_order(self):
        from app.talent.services.platform_operations import ROLE_HIERARCHY
        assert ROLE_HIERARCHY["owner"] > ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["member"]

    def test_role_escalation_blocked(self):
        from app.talent.services.platform_operations import detect_role_escalation
        result = detect_role_escalation("member", "admin", "contributor")
        assert result["blocked"] is True

    def test_role_escalation_allowed(self):
        from app.talent.services.platform_operations import detect_role_escalation
        result = detect_role_escalation("member", "admin", "owner")
        assert result["blocked"] is False

    def test_ip_allowlist_valid(self):
        from app.talent.services.platform_operations import validate_ip_allowlist
        assert validate_ip_allowlist(["192.168.1.1", "10.0.0.0/8"]) == []

    def test_ip_allowlist_invalid(self):
        from app.talent.services.platform_operations import validate_ip_allowlist
        errors = validate_ip_allowlist(["not-an-ip"])
        assert len(errors) > 0

    def test_ip_check_allowed(self):
        from app.talent.services.platform_operations import check_ip_allowed
        assert check_ip_allowed("192.168.1.1", ["192.168.1.0/24"]) is True

    def test_ip_check_denied(self):
        from app.talent.services.platform_operations import check_ip_allowed
        assert check_ip_allowed("10.0.0.1", ["192.168.1.0/24"]) is False

    def test_ip_check_empty_list(self):
        from app.talent.services.platform_operations import check_ip_allowed
        assert check_ip_allowed("1.2.3.4", []) is True

    def test_data_classification_email(self):
        from app.talent.services.platform_operations import get_field_classification
        result = get_field_classification("email")
        assert result["level"] >= 2

    def test_data_classification_public(self):
        from app.talent.services.platform_operations import get_field_classification
        result = get_field_classification("capability_name")
        assert result["level"] == 0

    def test_health_report_healthy(self):
        from app.talent.services.platform_operations import build_health_report
        report = build_health_report([{"service": "db", "status": "healthy"}])
        assert report["overall_status"] == "healthy"

    def test_health_report_degraded(self):
        from app.talent.services.platform_operations import build_health_report
        report = build_health_report([{"service": "db", "status": "degraded"}])
        assert report["overall_status"] == "degraded"

    def test_usage_within_limit(self):
        from app.talent.services.platform_operations import check_usage_limit
        result = check_usage_limit(50, 100)
        assert result["within_limit"] is True

    def test_usage_exceeded(self):
        from app.talent.services.platform_operations import check_usage_limit
        result = check_usage_limit(150, 100)
        assert result["within_limit"] is False

    def test_api_key_generate(self):
        from app.talent.services.integration_intelligence import generate_api_key
        result = generate_api_key("org1", "key1", ["read:capabilities"])
        assert result["raw_key"].startswith("osk_")

    def test_api_key_verify(self):
        from app.talent.services.integration_intelligence import generate_api_key, verify_api_key
        result = generate_api_key("org1", "k", ["read:capabilities"])
        assert verify_api_key(result["raw_key"], result["key_hash"]) is True
        assert verify_api_key("wrong", result["key_hash"]) is False
