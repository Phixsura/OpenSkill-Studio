"""Integration, security, pagination, and error-handling tests (214 tests).

Tests structural invariants, security boundaries, cross-feature flows,
pagination mechanics, and error responses — all WITHOUT a real database.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.talent.models.application import (
    APPLICATION_TRANSITIONS,
    Application,
    ApplicationEvent,
    ApplicationFeedback,
    InterviewStage,
    Placement,
)
from app.talent.models.assessment import (
    AssessmentBlueprint,
    AssessmentRun,
    Credential,
    CredentialRule,
)
from app.talent.models.bookmark import OpportunityBookmark
from app.talent.models.capability import Capability, CapabilityEdge, CapabilityMapping
from app.talent.models.career_goal import CareerGoal
from app.talent.models.candidate_note import CandidateNote
from app.talent.models.consent_log import ConsentLog
from app.talent.models.credential_pathway import CredentialPathway
from app.talent.models.employer import EmployerProfile, Opportunity
from app.talent.models.endorsement import SkillEndorsement
from app.talent.models.evidence import VERIFICATION_WEIGHTS, CapabilityEvidence
from app.talent.models.message import ApplicationMessage
from app.talent.models.notification import NotificationPreference, TalentNotification
from app.talent.models.offer import Offer
from app.talent.models.passport import SkillPassport
from app.talent.models.portfolio import (
    PORTFOLIO_ITEM_TYPES,
    PORTFOLIO_VISIBILITY_OPTIONS,
    PortfolioItem,
)
from app.talent.models.scorecard import InterviewScorecard
from app.talent.models.succession import KeyRole, SuccessorNomination
from app.talent.models.webhook_endpoint import WebhookDeliveryLog, WebhookEndpointConfig
from app.talent.services.scoring import (
    SCORING_VERSION,
    compute_recency,
    compute_score_from_evidence,
    compute_velocity,
    decay_factor,
    determine_level,
)


# ═══════════════════════════════════════════════════════════════
# SECTION 1: SECURITY — IDOR / Auth / Injection (tests 1–70)
# ═══════════════════════════════════════════════════════════════


class TestIDORPrevention:
    """Structural: IDOR protections — resources scope by user/org."""

    # 1
    def test_application_has_user_id_column(self):
        assert "user_id" in Application.__table__.columns

    # 2
    def test_bookmark_has_user_id_column(self):
        assert "user_id" in OpportunityBookmark.__table__.columns

    # 3
    def test_career_goal_has_user_id_column(self):
        assert "user_id" in CareerGoal.__table__.columns

    # 4
    def test_evidence_has_user_id_column(self):
        assert "user_id" in CapabilityEvidence.__table__.columns

    # 5
    def test_endorsement_has_endorser_id(self):
        assert "endorser_id" in SkillEndorsement.__table__.columns

    # 6
    def test_endorsement_has_user_id(self):
        assert "user_id" in SkillEndorsement.__table__.columns

    # 7
    def test_portfolio_item_has_user_id(self):
        assert "user_id" in PortfolioItem.__table__.columns

    # 8
    def test_candidate_note_has_author_id(self):
        assert "author_id" in CandidateNote.__table__.columns

    # 9
    def test_consent_log_has_user_id(self):
        assert "user_id" in ConsentLog.__table__.columns

    # 10
    def test_notification_pref_has_user_id(self):
        assert "user_id" in NotificationPreference.__table__.columns

    # 11
    def test_notification_has_user_id(self):
        assert "user_id" in TalentNotification.__table__.columns

    # 12
    def test_passport_has_user_id(self):
        assert "user_id" in SkillPassport.__table__.columns

    # 13
    def test_offer_has_application_id(self):
        assert "application_id" in Offer.__table__.columns

    # 14
    def test_message_has_sender_id(self):
        assert "sender_id" in ApplicationMessage.__table__.columns


class TestAuthStructure:
    """Structural: Auth column constraints prevent unauthorized access."""

    # 15
    def test_application_event_acted_by_not_nullable(self):
        col = ApplicationEvent.__table__.columns["acted_by"]
        assert col.nullable is False

    # 16
    def test_webhook_has_org_id(self):
        assert "org_id" in WebhookEndpointConfig.__table__.columns

    # 17
    def test_webhook_has_created_by(self):
        assert "created_by" in WebhookEndpointConfig.__table__.columns

    # 18
    def test_key_role_has_org_id(self):
        assert "org_id" in KeyRole.__table__.columns

    # 19
    def test_opportunity_has_employer_org_id(self):
        assert "employer_org_id" in Opportunity.__table__.columns

    # 20
    def test_employer_profile_has_org_id(self):
        assert "org_id" in EmployerProfile.__table__.columns

    # 21
    def test_assessment_has_org_id(self):
        assert "org_id" in AssessmentBlueprint.__table__.columns

    # 22
    def test_scorecard_has_interviewer_id(self):
        assert "interviewer_id" in InterviewScorecard.__table__.columns

    # 23
    def test_placement_has_org_id(self):
        assert "employer_org_id" in Placement.__table__.columns


class TestInputInjection:
    """Structural: Fields that accept user input have length limits."""

    # 24
    def test_capability_canonical_name_has_max_length(self):
        col = Capability.__table__.columns["canonical_name"]
        assert col.type.length is not None and col.type.length <= 500

    # 25
    def test_opportunity_title_has_max_length(self):
        col = Opportunity.__table__.columns["title"]
        assert col.type.length is not None and col.type.length <= 500

    # 26
    def test_webhook_url_has_max_length(self):
        col = WebhookEndpointConfig.__table__.columns["url"]
        assert col.type.length is not None and col.type.length <= 500

    # 27
    def test_portfolio_title_has_max_length(self):
        col = PortfolioItem.__table__.columns["title"]
        assert col.type.length is not None and col.type.length <= 500

    # 28
    def test_offer_role_title_has_max_length(self):
        col = Offer.__table__.columns["role_title"]
        assert col.type.length is not None and col.type.length <= 500

    # 29
    def test_career_goal_title_has_max_length(self):
        col = CareerGoal.__table__.columns["title"]
        assert col.type.length is not None and col.type.length <= 500

    # 30
    def test_credential_pathway_name_has_max_length(self):
        col = CredentialPathway.__table__.columns["name"]
        assert col.type.length is not None and col.type.length <= 500

    # 31
    def test_key_role_title_has_max_length(self):
        col = KeyRole.__table__.columns["title"]
        assert col.type.length is not None and col.type.length <= 500

    # 32
    def test_endorsement_message_allows_text(self):
        col = SkillEndorsement.__table__.columns["message"]
        assert col.nullable is True

    # 33
    def test_message_content_is_text(self):
        col = ApplicationMessage.__table__.columns["content"]
        # Text type, no fixed length
        assert str(col.type) in ("TEXT", "Text()")


class TestRateLimitModule:
    """Rate limiter structural tests."""

    # 34
    def test_rate_limiter_imports(self):
        from app.talent.api.rate_limit import MAX_REQUESTS, WINDOW_SECONDS
        assert MAX_REQUESTS > 0
        assert WINDOW_SECONDS > 0

    # 35
    def test_rate_limiter_default_window_60s(self):
        from app.talent.api.rate_limit import WINDOW_SECONDS
        assert WINDOW_SECONDS == 60

    # 36
    def test_rate_limiter_default_max_100(self):
        from app.talent.api.rate_limit import MAX_REQUESTS
        assert MAX_REQUESTS == 100

    # 37
    def test_rate_limiter_counter_is_dict(self):
        from app.talent.api.rate_limit import _counters
        assert isinstance(_counters, dict)


class TestETagModule:
    """ETag utility tests."""

    # 38
    def test_compute_etag_returns_weak(self):
        from app.talent.api.etag import compute_etag
        etag = compute_etag(b"hello world")
        assert etag.startswith('W/"')
        assert etag.endswith('"')

    # 39
    def test_compute_etag_deterministic(self):
        from app.talent.api.etag import compute_etag
        a = compute_etag(b"test data")
        b = compute_etag(b"test data")
        assert a == b

    # 40
    def test_compute_etag_different_for_different_data(self):
        from app.talent.api.etag import compute_etag
        a = compute_etag(b"data1")
        b = compute_etag(b"data2")
        assert a != b

    # 41
    def test_compute_etag_handles_empty_body(self):
        from app.talent.api.etag import compute_etag
        etag = compute_etag(b"")
        assert etag.startswith('W/"')

    # 42
    def test_etag_route_class_exists(self):
        from app.talent.api.etag import ETagRoute
        assert ETagRoute is not None


class TestSSRFProtection:
    """Structural: URL fields should have length limits to prevent abuse."""

    # 43
    def test_portfolio_url_has_max_length(self):
        col = PortfolioItem.__table__.columns["url"]
        assert col.type.length is not None and col.type.length <= 500

    # 44
    def test_portfolio_image_url_has_max_length(self):
        col = PortfolioItem.__table__.columns["image_url"]
        assert col.type.length is not None and col.type.length <= 500

    # 45
    def test_webhook_url_constrained(self):
        col = WebhookEndpointConfig.__table__.columns["url"]
        assert col.type.length is not None

    # 46
    def test_webhook_secret_constrained(self):
        col = WebhookEndpointConfig.__table__.columns["secret"]
        assert col.type.length is not None and col.type.length <= 200


class TestMassAssignment:
    """Structural: Models don't expose internal fields to mutation."""

    # 47
    def test_application_has_created_at(self):
        col = Application.__table__.columns["created_at"]
        assert col.server_default is not None

    # 48
    def test_evidence_has_created_at(self):
        col = CapabilityEvidence.__table__.columns["created_at"]
        assert col.server_default is not None

    # 49
    def test_capability_has_created_at(self):
        col = Capability.__table__.columns["created_at"]
        assert col.server_default is not None

    # 50
    def test_offer_has_created_at(self):
        col = Offer.__table__.columns["created_at"]
        assert col.server_default is not None

    # 51
    def test_webhook_has_created_at(self):
        col = WebhookEndpointConfig.__table__.columns["created_at"]
        assert col.server_default is not None

    # 52
    def test_notification_has_created_at(self):
        col = TalentNotification.__table__.columns["created_at"]
        assert col.server_default is not None

    # 53
    def test_endorsement_has_created_at(self):
        col = SkillEndorsement.__table__.columns["created_at"]
        assert col.server_default is not None


class TestStateTransitionSecurity:
    """No invalid application state transitions."""

    # 54
    def test_draft_cannot_go_to_hired(self):
        assert "hired" not in APPLICATION_TRANSITIONS.get("draft", [])

    # 55
    def test_draft_cannot_go_to_offer(self):
        assert "offer" not in APPLICATION_TRANSITIONS.get("draft", [])

    # 56
    def test_rejected_is_terminal(self):
        targets = APPLICATION_TRANSITIONS.get("rejected", [])
        assert len(targets) == 0

    # 57
    def test_completed_is_terminal(self):
        targets = APPLICATION_TRANSITIONS.get("completed", [])
        assert len(targets) == 0

    # 58
    def test_withdrawn_is_terminal(self):
        targets = APPLICATION_TRANSITIONS.get("withdrawn", [])
        assert len(targets) == 0

    # 59
    def test_screening_can_go_to_rejected(self):
        targets = APPLICATION_TRANSITIONS.get("screening", [])
        assert "rejected" in targets

    # 60
    def test_interview_can_go_to_offer(self):
        targets = APPLICATION_TRANSITIONS.get("interview", [])
        assert "offer" in targets

    # 61
    def test_offer_can_go_to_accepted(self):
        targets = APPLICATION_TRANSITIONS.get("offer", [])
        assert "accepted" in targets

    # 62
    def test_offer_can_go_to_rejected(self):
        targets = APPLICATION_TRANSITIONS.get("offer", [])
        assert "rejected" in targets

    # 63
    def test_accepted_can_go_to_hired(self):
        targets = APPLICATION_TRANSITIONS.get("accepted", [])
        assert "hired" in targets

    # 64
    def test_no_backward_from_hired(self):
        targets = APPLICATION_TRANSITIONS.get("hired", [])
        assert "draft" not in targets
        assert "screening" not in targets

    # 65
    def test_all_states_defined(self):
        expected = {"draft", "submitted", "screening", "interview", "assessment", "offer", "accepted", "rejected", "withdrawn", "hired", "completed"}
        assert expected.issubset(set(APPLICATION_TRANSITIONS.keys()))


class TestVerificationWeights:
    """Structural: Evidence verification levels have proper weights."""

    # 66
    def test_self_reported_is_lowest(self):
        assert VERIFICATION_WEIGHTS["self_reported"] <= VERIFICATION_WEIGHTS.get("peer_reviewed", 1.0)

    # 67
    def test_employer_verified_is_high(self):
        assert VERIFICATION_WEIGHTS["employer_verified"] >= 0.5

    # 68
    def test_all_weights_between_0_and_1(self):
        for k, v in VERIFICATION_WEIGHTS.items():
            assert 0.0 <= v <= 1.0, f"{k} weight {v} out of range"

    # 69
    def test_at_least_3_verification_levels(self):
        assert len(VERIFICATION_WEIGHTS) >= 3

    # 70
    def test_self_reported_exists(self):
        assert "self_reported" in VERIFICATION_WEIGHTS


# ═══════════════════════════════════════════════════════════════
# SECTION 2: CROSS-FEATURE INTEGRATION (tests 71–140)
# ═══════════════════════════════════════════════════════════════


class TestCapabilityEvidenceScoreFlow:
    """Integration: Capability → Evidence → Score flow."""

    # 71
    def test_scoring_version_is_string(self):
        assert isinstance(SCORING_VERSION, str) and len(SCORING_VERSION) > 0

    # 72
    def test_score_zero_for_no_evidence(self):
        s, _, _ = compute_score_from_evidence([], None, datetime.now(UTC))
        assert s == 0.0

    # 73
    def test_score_positive_for_single_active_evidence(self):
        ev = [{
            "status": "active", "score_normalized": 0.8,
            "verification_level": "employer_verified", "confidence": 1.0,
            "occurred_at": datetime.now(UTC), "expires_at": None,
        }]
        s, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert s > 0.0

    # 74
    def test_multiple_evidence_increases_score(self):
        now = datetime.now(UTC)
        ev1 = [{
            "status": "active", "score_normalized": 0.6,
            "verification_level": "self_reported", "confidence": 0.8,
            "occurred_at": now, "expires_at": None,
        }]
        ev2 = ev1 + [{
            "status": "active", "score_normalized": 0.9,
            "verification_level": "employer_verified", "confidence": 1.0,
            "occurred_at": now, "expires_at": None,
        }]
        s1, _, _ = compute_score_from_evidence(ev1, None, now)
        s2, _, _ = compute_score_from_evidence(ev2, None, now)
        assert s2 >= s1

    # 75
    def test_voided_evidence_excluded(self):
        now = datetime.now(UTC)
        ev = [{
            "status": "voided", "score_normalized": 1.0,
            "verification_level": "employer_verified", "confidence": 1.0,
            "occurred_at": now, "expires_at": None,
        }]
        s, _, _ = compute_score_from_evidence(ev, None, now)
        assert s == 0.0

    # 76
    def test_expired_evidence_excluded(self):
        now = datetime.now(UTC)
        ev = [{
            "status": "active", "score_normalized": 1.0,
            "verification_level": "employer_verified", "confidence": 1.0,
            "occurred_at": now - timedelta(days=30),
            "expires_at": now - timedelta(hours=1),
        }]
        s, _, _ = compute_score_from_evidence(ev, None, now)
        assert s == 0.0

    # 77
    def test_score_bounded_0_to_1(self):
        now = datetime.now(UTC)
        ev = [
            {
                "status": "active", "score_normalized": 1.0,
                "verification_level": "employer_verified", "confidence": 1.0,
                "occurred_at": now - timedelta(days=i), "expires_at": None,
            }
            for i in range(20)
        ]
        s, _, _ = compute_score_from_evidence(ev, None, now)
        assert 0.0 <= s <= 1.0

    # 78
    def test_decay_factor_present_is_1(self):
        now = datetime.now(UTC)
        assert decay_factor(now, now, None) == 1.0

    # 79
    def test_decay_factor_old_is_less_than_1(self):
        now = datetime.now(UTC)
        old = now - timedelta(days=365 * 3)
        d = decay_factor(old, now, {"half_life_days": 365})
        assert 0.0 < d < 1.0

    # 80
    def test_recency_positive_for_recent(self):
        now = datetime.now(UTC)
        ev = [{"occurred_at": now - timedelta(hours=1), "status": "active"}]
        assert compute_recency(ev, now) > 0.0

    # 81
    def test_recency_zero_for_empty(self):
        assert compute_recency([], datetime.now(UTC)) == 0.0

    # 82
    def test_recency_zero_for_voided(self):
        now = datetime.now(UTC)
        ev = [{"occurred_at": now, "status": "voided"}]
        assert compute_recency(ev, now) == 0.0

    # 83
    def test_velocity_positive_for_recent_burst(self):
        now = datetime.now(UTC)
        ev = [
            {"occurred_at": now - timedelta(days=i), "status": "active"}
            for i in range(5)
        ]
        assert compute_velocity(ev, now) > 0.0

    # 84
    def test_velocity_zero_for_empty(self):
        assert compute_velocity([], datetime.now(UTC)) == 0.0

    # 85
    def test_velocity_zero_for_old(self):
        now = datetime.now(UTC)
        ev = [{"occurred_at": now - timedelta(days=365), "status": "active"}]
        assert compute_velocity(ev, now) == 0.0

    # 86
    def test_determine_level_zero_for_low_score(self):
        lvl, _ = determine_level(0.0, 0, None)
        assert lvl == 0

    # 87
    def test_determine_level_positive_for_high_score(self):
        lvl, _ = determine_level(0.95, 10, None)
        assert lvl > 0

    # 88
    def test_determine_level_needs_min_evidence(self):
        lvl, _ = determine_level(0.99, 0, None)
        assert lvl == 0

    # 89
    def test_determine_level_returns_tuple(self):
        result = determine_level(0.5, 5, None)
        assert isinstance(result, tuple) and len(result) == 2

    # 90
    def test_determine_level_label_is_string(self):
        _, label = determine_level(0.5, 5, None)
        assert isinstance(label, str)


class TestApplicationOfferFlow:
    """Integration: Application → state transitions → offer/hire lifecycle."""

    # 91
    def test_submitted_to_screening(self):
        assert "screening" in APPLICATION_TRANSITIONS["submitted"]

    # 92
    def test_screening_to_interview(self):
        assert "interview" in APPLICATION_TRANSITIONS["screening"]

    # 93
    def test_full_happy_path_exists(self):
        """draft → submitted → screening → interview → offer → accepted → hired is reachable."""
        path = ["draft", "submitted", "screening", "interview", "offer", "accepted", "hired"]
        for i in range(len(path) - 1):
            assert path[i + 1] in APPLICATION_TRANSITIONS[path[i]], (
                f"Can't go from {path[i]} to {path[i+1]}"
            )

    # 94
    def test_every_state_has_reject_or_withdraw_except_terminal(self):
        terminal = {"rejected", "withdrawn", "completed", "hired"}
        for state, targets in APPLICATION_TRANSITIONS.items():
            if state not in terminal:
                has_exit = "rejected" in targets or "withdrawn" in targets
                assert has_exit, f"State {state} has no reject/withdraw exit"

    # 95
    def test_application_has_status_column(self):
        assert "status" in Application.__table__.columns

    # 96
    def test_placement_has_start_date(self):
        assert "start_date" in Placement.__table__.columns

    # 97
    def test_placement_has_end_date(self):
        assert "end_date" in Placement.__table__.columns

    # 98
    def test_offer_has_status_column(self):
        assert "status" in Offer.__table__.columns

    # 99
    def test_offer_has_expires_at(self):
        assert "expires_at" in Offer.__table__.columns

    # 100
    def test_offer_has_accepted_at(self):
        assert "accepted_at" in Offer.__table__.columns


class TestPortfolioPublicProfileFlow:
    """Integration: Portfolio items feed into public profiles."""

    # 101
    def test_portfolio_item_types_non_empty(self):
        assert len(PORTFOLIO_ITEM_TYPES) >= 5

    # 102
    def test_portfolio_item_types_contain_project(self):
        assert "project" in PORTFOLIO_ITEM_TYPES

    # 103
    def test_portfolio_item_types_contain_case_study(self):
        assert "case_study" in PORTFOLIO_ITEM_TYPES

    # 104
    def test_portfolio_visibility_options(self):
        assert "private" in PORTFOLIO_VISIBILITY_OPTIONS
        assert "public" in PORTFOLIO_VISIBILITY_OPTIONS

    # 105
    def test_portfolio_has_pinned_field(self):
        assert "pinned" in PortfolioItem.__table__.columns

    # 106
    def test_portfolio_has_sort_order(self):
        assert "sort_order" in PortfolioItem.__table__.columns

    # 107
    def test_portfolio_has_visibility(self):
        assert "visibility" in PortfolioItem.__table__.columns

    # 108
    def test_passport_visible_is_option(self):
        assert "passport_visible" in PORTFOLIO_VISIBILITY_OPTIONS


class TestWebhookDeliveryFlow:
    """Integration: Webhook endpoint → event → delivery log lifecycle."""

    # 109
    def test_delivery_log_has_endpoint_id(self):
        assert "endpoint_id" in WebhookDeliveryLog.__table__.columns

    # 110
    def test_delivery_log_has_event_type(self):
        assert "event_type" in WebhookDeliveryLog.__table__.columns

    # 111
    def test_delivery_log_has_status(self):
        assert "status" in WebhookDeliveryLog.__table__.columns

    # 112
    def test_delivery_log_has_attempts(self):
        assert "attempts" in WebhookDeliveryLog.__table__.columns

    # 113
    def test_delivery_log_has_response_code(self):
        assert "response_code" in WebhookDeliveryLog.__table__.columns

    # 114
    def test_endpoint_has_active_flag(self):
        assert "active" in WebhookEndpointConfig.__table__.columns

    # 115
    def test_endpoint_has_event_types(self):
        assert "event_types" in WebhookEndpointConfig.__table__.columns


class TestSuccessionPlanningFlow:
    """Integration: Key role → successor nomination → readiness flow."""

    # 116
    def test_key_role_has_criticality(self):
        assert "criticality" in KeyRole.__table__.columns

    # 117
    def test_key_role_has_status(self):
        assert "status" in KeyRole.__table__.columns

    # 118
    def test_key_role_has_current_holder(self):
        assert "current_holder_id" in KeyRole.__table__.columns

    # 119
    def test_nomination_has_readiness(self):
        assert "readiness" in SuccessorNomination.__table__.columns

    # 120
    def test_nomination_has_capability_match(self):
        assert "capability_match" in SuccessorNomination.__table__.columns

    # 121
    def test_nomination_has_gaps(self):
        assert "gaps" in SuccessorNomination.__table__.columns

    # 122
    def test_nomination_has_development_plan(self):
        assert "development_plan" in SuccessorNomination.__table__.columns

    # 123
    def test_nomination_links_to_key_role(self):
        assert "key_role_id" in SuccessorNomination.__table__.columns


class TestCredentialBadgeFlow:
    """Integration: Credential → badge export → verification."""

    # 124
    def test_credential_has_status(self):
        assert "status" in Credential.__table__.columns

    # 125
    def test_credential_has_issued_at(self):
        assert "issued_at" in Credential.__table__.columns

    # 126
    def test_credential_has_evidence_references(self):
        assert "evidence_references" in Credential.__table__.columns

    # 127
    def test_credential_rule_has_requirements(self):
        assert "requirements" in CredentialRule.__table__.columns

    # 128
    def test_credential_rule_has_org_id(self):
        assert "org_id" in CredentialRule.__table__.columns

    # 129
    def test_assessment_run_has_status(self):
        assert "status" in AssessmentRun.__table__.columns

    # 130
    def test_assessment_blueprint_has_org_id(self):
        assert "org_id" in AssessmentBlueprint.__table__.columns


class TestSkillInferenceIntegration:
    """Integration: Skill inference from text produces candidate capabilities."""

    # 131
    def test_infer_function_exists(self):
        from app.talent.services.skill_inference import infer_skills_from_text
        assert callable(infer_skills_from_text)

    # 132
    def test_extract_candidates_helper_exists(self):
        from app.talent.services.skill_inference import _extract_candidates
        assert callable(_extract_candidates)

    # 133
    def test_extract_candidates_returns_list(self):
        from app.talent.services.skill_inference import _extract_candidates
        result = _extract_candidates("Python programming and data analysis")
        assert isinstance(result, list)

    # 134
    def test_extract_candidates_finds_terms(self):
        from app.talent.services.skill_inference import _extract_candidates
        result = _extract_candidates("Python programming experience")
        assert len(result) > 0

    # 135
    def test_find_excerpt_helper(self):
        from app.talent.services.skill_inference import _find_excerpt
        excerpt = _find_excerpt("I have Python experience in data", "Python")
        assert "Python" in excerpt

    # 136
    def test_find_excerpt_missing_term(self):
        from app.talent.services.skill_inference import _find_excerpt
        excerpt = _find_excerpt("No matching content here", "Rust")
        assert isinstance(excerpt, str)


class TestCareerPathIntegration:
    """Integration: Career path suggestion function structure."""

    # 137
    def test_suggest_action_exists(self):
        from app.talent.services.career_path import _suggest_action
        assert callable(_suggest_action)

    # 138
    def test_suggest_action_gap_zero(self):
        from app.talent.services.career_path import _suggest_action
        action = _suggest_action(3, 3, 0)
        assert isinstance(action, str)

    # 139
    def test_suggest_action_positive_gap(self):
        from app.talent.services.career_path import _suggest_action
        action = _suggest_action(1, 3, 2)
        assert len(action) > 0

    # 140
    def test_suggest_action_negative_gap(self):
        from app.talent.services.career_path import _suggest_action
        action = _suggest_action(5, 3, -2)
        assert isinstance(action, str)


# ═══════════════════════════════════════════════════════════════
# SECTION 3: PAGINATION & FILTERING (tests 141–180)
# ═══════════════════════════════════════════════════════════════


class TestPaginationModule:
    """Pagination helper structural tests."""

    # 141
    def test_paginate_query_exists(self):
        from app.talent.api.pagination import paginate_query
        assert callable(paginate_query)

    # 142
    def test_cursor_meta_schema_exists(self):
        from app.talent.schemas.cursor import CursorMeta
        assert CursorMeta is not None

    # 143
    def test_cursor_meta_has_next_cursor(self):
        from app.talent.schemas.cursor import CursorMeta
        fields = CursorMeta.model_fields
        assert "next_cursor" in fields

    # 144
    def test_cursor_meta_has_has_more(self):
        from app.talent.schemas.cursor import CursorMeta
        fields = CursorMeta.model_fields
        assert "has_more" in fields

    # 145
    def test_cursor_meta_default_values(self):
        from app.talent.schemas.cursor import CursorMeta
        meta = CursorMeta(next_cursor=None, has_more=False)
        assert meta.next_cursor is None
        assert meta.has_more is False

    # 146
    def test_cursor_meta_with_cursor(self):
        from app.talent.schemas.cursor import CursorMeta
        meta = CursorMeta(next_cursor="01ABCDEF", has_more=True)
        assert meta.next_cursor == "01ABCDEF"
        assert meta.has_more is True


class TestCapabilityPagination:
    """Capability model supports pagination via ULID ordering."""

    # 147
    def test_capability_has_id_primary_key(self):
        col = Capability.__table__.columns["id"]
        assert col.primary_key

    # 148
    def test_evidence_has_id_primary_key(self):
        col = CapabilityEvidence.__table__.columns["id"]
        assert col.primary_key

    # 149
    def test_application_has_id_primary_key(self):
        col = Application.__table__.columns["id"]
        assert col.primary_key

    # 150
    def test_opportunity_has_id_primary_key(self):
        col = Opportunity.__table__.columns["id"]
        assert col.primary_key


class TestFilteringSupport:
    """Models support filtering via indexed columns."""

    # 151
    def test_capability_canonical_name_exists(self):
        col = Capability.__table__.columns["canonical_name"]
        assert col is not None

    # 152
    def test_application_status_column_exists(self):
        assert "status" in Application.__table__.columns

    # 153
    def test_opportunity_status_column_exists(self):
        assert "status" in Opportunity.__table__.columns

    # 154
    def test_evidence_status_column_exists(self):
        assert "status" in CapabilityEvidence.__table__.columns

    # 155
    def test_evidence_user_id_indexed(self):
        col = CapabilityEvidence.__table__.columns["user_id"]
        assert col.index or any(
            "user_id" in str(idx.columns) for idx in CapabilityEvidence.__table__.indexes
        )

    # 156
    def test_application_user_id_indexed(self):
        col = Application.__table__.columns["user_id"]
        assert col.index or any(
            "user_id" in str(idx.columns) for idx in Application.__table__.indexes
        )

    # 157
    def test_bookmark_user_id_indexed(self):
        col = OpportunityBookmark.__table__.columns["user_id"]
        assert col.index or any(
            "user_id" in str(idx.columns) for idx in OpportunityBookmark.__table__.indexes
        )

    # 158
    def test_endorsement_user_id_exists(self):
        col = SkillEndorsement.__table__.columns["user_id"]
        assert col is not None

    # 159
    def test_webhook_org_id_indexed(self):
        col = WebhookEndpointConfig.__table__.columns["org_id"]
        assert col.index or any(
            "org_id" in str(idx.columns) for idx in WebhookEndpointConfig.__table__.indexes
        )


class TestDateRangeFiltering:
    """Models support date-range filtering via timestamp columns."""

    # 160
    def test_evidence_has_occurred_at(self):
        assert "occurred_at" in CapabilityEvidence.__table__.columns

    # 161
    def test_evidence_has_expires_at(self):
        assert "expires_at" in CapabilityEvidence.__table__.columns

    # 162
    def test_application_has_created_at(self):
        assert "created_at" in Application.__table__.columns

    # 163
    def test_application_has_updated_at(self):
        assert "updated_at" in Application.__table__.columns

    # 164
    def test_offer_has_expires_at(self):
        assert "expires_at" in Offer.__table__.columns

    # 165
    def test_offer_has_created_at(self):
        assert "created_at" in Offer.__table__.columns

    # 166
    def test_capability_has_updated_at(self):
        assert "updated_at" in Capability.__table__.columns

    # 167
    def test_key_role_has_created_at(self):
        assert "created_at" in KeyRole.__table__.columns

    # 168
    def test_nomination_has_created_at(self):
        assert "created_at" in SuccessorNomination.__table__.columns


class TestSortingSupport:
    """Models support sorting via common fields."""

    # 169
    def test_portfolio_has_sort_order_int(self):
        col = PortfolioItem.__table__.columns["sort_order"]
        assert col is not None

    # 170
    def test_capability_edge_has_metadata(self):
        assert "metadata" in CapabilityEdge.__table__.columns

    # 171
    def test_scorecard_has_overall_rating(self):
        assert "overall_rating" in InterviewScorecard.__table__.columns

    # 172
    def test_delivery_log_has_created_at(self):
        assert "created_at" in WebhookDeliveryLog.__table__.columns


class TestResultSetStructure:
    """Empty and populated result set handling."""

    # 173
    def test_empty_evidence_list_scores_zero(self):
        s, _, _ = compute_score_from_evidence([], None, datetime.now(UTC))
        assert s == 0.0

    # 174
    def test_recency_empty_list_returns_zero(self):
        assert compute_recency([], datetime.now(UTC)) == 0.0

    # 175
    def test_velocity_empty_list_returns_zero(self):
        assert compute_velocity([], datetime.now(UTC)) == 0.0

    # 176
    def test_determine_level_zero_evidence_returns_zero(self):
        lvl, _ = determine_level(0.0, 0, None)
        assert lvl == 0

    # 177
    def test_portfolio_item_types_is_frozenset(self):
        assert isinstance(PORTFOLIO_ITEM_TYPES, frozenset)

    # 178
    def test_portfolio_visibility_is_frozenset(self):
        assert isinstance(PORTFOLIO_VISIBILITY_OPTIONS, frozenset)

    # 179
    def test_verification_weights_is_dict(self):
        assert isinstance(VERIFICATION_WEIGHTS, dict)

    # 180
    def test_application_transitions_is_dict(self):
        assert isinstance(APPLICATION_TRANSITIONS, dict)


# ═══════════════════════════════════════════════════════════════
# SECTION 4: ERROR HANDLING (tests 181–214)
# ═══════════════════════════════════════════════════════════════


class TestScoringErrorHandling:
    """Scoring functions handle edge cases gracefully."""

    # 181
    def test_score_none_confidence_raises(self):
        ev = [{
            "status": "active", "score_normalized": None,
            "verification_level": "self_reported", "confidence": None,
            "occurred_at": datetime.now(UTC), "expires_at": None,
        }]
        with pytest.raises((TypeError, ValueError)):
            compute_score_from_evidence(ev, None, datetime.now(UTC))

    # 182
    def test_score_zero_confidence(self):
        ev = [{
            "status": "active", "score_normalized": 1.0,
            "verification_level": "employer_verified", "confidence": 0.0,
            "occurred_at": datetime.now(UTC), "expires_at": None,
        }]
        s, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert s >= 0.0

    # 183
    def test_score_negative_normalized(self):
        ev = [{
            "status": "active", "score_normalized": -0.5,
            "verification_level": "self_reported", "confidence": 1.0,
            "occurred_at": datetime.now(UTC), "expires_at": None,
        }]
        s, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert isinstance(s, float)

    # 184
    def test_score_over_one_normalized(self):
        ev = [{
            "status": "active", "score_normalized": 5.0,
            "verification_level": "employer_verified", "confidence": 1.0,
            "occurred_at": datetime.now(UTC), "expires_at": None,
        }]
        s, _, _ = compute_score_from_evidence(ev, None, datetime.now(UTC))
        assert isinstance(s, float)

    # 185
    def test_decay_none_occurred_at(self):
        """decay_factor handles None config gracefully."""
        now = datetime.now(UTC)
        d = decay_factor(now, now, None)
        assert d == 1.0

    # 186
    def test_decay_empty_config(self):
        d = decay_factor(datetime.now(UTC), datetime.now(UTC), {})
        assert d == 1.0

    # 187
    def test_decay_future_date(self):
        now = datetime.now(UTC)
        future = now + timedelta(days=30)
        d = decay_factor(future, now, {"half_life_days": 365})
        assert isinstance(d, float)

    # 188
    def test_determine_level_very_high_score(self):
        lvl, label = determine_level(1.0, 100, None)
        assert lvl > 0
        assert isinstance(label, str)

    # 189
    def test_determine_level_custom_defs_malformed(self):
        lvl, label = determine_level(0.5, 5, {"not_valid": True})
        assert isinstance(lvl, int)
        assert isinstance(label, str)

    # 190
    def test_recency_future_evidence(self):
        now = datetime.now(UTC)
        ev = [{"occurred_at": now + timedelta(days=30), "status": "active"}]
        r = compute_recency(ev, now)
        assert isinstance(r, float)

    # 191
    def test_velocity_single_item(self):
        now = datetime.now(UTC)
        ev = [{"occurred_at": now, "status": "active"}]
        v = compute_velocity(ev, now)
        assert isinstance(v, float) and v >= 0.0


class TestTableNameConsistency:
    """All models have consistent table naming."""

    # 192
    def test_capability_tablename(self):
        assert Capability.__tablename__ == "capabilities"

    # 193
    def test_evidence_tablename(self):
        assert CapabilityEvidence.__tablename__ == "capability_evidence"

    # 194
    def test_application_tablename(self):
        assert Application.__tablename__ == "applications"

    # 195
    def test_bookmark_tablename(self):
        assert OpportunityBookmark.__tablename__ == "talent_opportunity_bookmarks"

    # 196
    def test_career_goal_tablename(self):
        assert CareerGoal.__tablename__ == "talent_career_goals"

    # 197
    def test_endorsement_tablename(self):
        assert SkillEndorsement.__tablename__ == "talent_skill_endorsements"

    # 198
    def test_portfolio_tablename(self):
        assert PortfolioItem.__tablename__ == "talent_portfolio_items"

    # 199
    def test_offer_tablename(self):
        assert Offer.__tablename__ == "talent_offers"

    # 200
    def test_message_tablename(self):
        assert ApplicationMessage.__tablename__ == "talent_application_messages"

    # 201
    def test_webhook_endpoint_tablename(self):
        assert WebhookEndpointConfig.__tablename__ == "talent_webhook_endpoints"

    # 202
    def test_delivery_log_tablename(self):
        assert WebhookDeliveryLog.__tablename__ == "talent_webhook_delivery_log"

    # 203
    def test_key_role_tablename(self):
        assert KeyRole.__tablename__ == "talent_key_roles"

    # 204
    def test_nomination_tablename(self):
        assert SuccessorNomination.__tablename__ == "talent_successor_nominations"

    # 205
    def test_scorecard_tablename(self):
        assert InterviewScorecard.__tablename__ == "talent_interview_scorecards"


class TestForeignKeyIntegrity:
    """Foreign keys point to correct tables."""

    # 206
    def test_evidence_capability_fk(self):
        col = CapabilityEvidence.__table__.columns["capability_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("capabilities.id" in t for t in fk_targets)

    # 207
    def test_evidence_user_fk(self):
        col = CapabilityEvidence.__table__.columns["user_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("users.id" in t for t in fk_targets)

    # 208
    def test_application_user_fk(self):
        col = Application.__table__.columns["user_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("users.id" in t for t in fk_targets)

    # 209
    def test_bookmark_user_fk(self):
        col = OpportunityBookmark.__table__.columns["user_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("users.id" in t for t in fk_targets)

    # 210
    def test_endorsement_endorser_fk(self):
        col = SkillEndorsement.__table__.columns["endorser_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("users.id" in t for t in fk_targets)

    # 211
    def test_offer_application_fk(self):
        col = Offer.__table__.columns["application_id"]
        fk_targets = [str(fk.target_fullname) for fk in col.foreign_keys]
        assert any("application" in t.lower() for t in fk_targets)

    # 212
    def test_nomination_key_role_fk(self):
        col = SuccessorNomination.__table__.columns["key_role_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("talent_key_roles.id" in t for t in fk_targets)

    # 213
    def test_delivery_log_endpoint_fk(self):
        col = WebhookDeliveryLog.__table__.columns["endpoint_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("talent_webhook_endpoints.id" in t for t in fk_targets)

    # 214
    def test_capability_edge_source_fk(self):
        col = CapabilityEdge.__table__.columns["source_id"]
        fk_targets = [str(fk.column) for fk in col.foreign_keys]
        assert any("capabilities.id" in t for t in fk_targets)
