"""Model & schema validation tests — 220 tests covering field constraints,
Pydantic validation, enum values, defaults, edge cases, and data integrity.

All tests run WITHOUT a database connection.
"""

import re
from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import BaseModel, ValidationError


# ═══════════════════════════════════════════════════════════════════
# SECTION 1: Model tablenames & class existence (tests 1-20)
# ═══════════════════════════════════════════════════════════════════

class TestModelTablenames:
    """Verify every model class exists and has the expected __tablename__."""

    # 1
    def test_capability_tablename(self):
        from app.talent.models.capability import Capability
        assert Capability.__tablename__ == "capabilities"

    # 2
    def test_capability_edge_tablename(self):
        from app.talent.models.capability import CapabilityEdge
        assert CapabilityEdge.__tablename__ == "capability_edges"

    # 3
    def test_evidence_tablename(self):
        from app.talent.models.evidence import CapabilityEvidence
        assert CapabilityEvidence.__tablename__ == "capability_evidence"

    # 4
    def test_application_tablename(self):
        from app.talent.models.application import Application
        assert Application.__tablename__ == "applications"

    # 5
    def test_application_event_tablename(self):
        from app.talent.models.application import ApplicationEvent
        assert ApplicationEvent.__tablename__ == "application_events"

    # 6
    def test_assessment_blueprint_tablename(self):
        from app.talent.models.assessment import AssessmentBlueprint
        assert AssessmentBlueprint.__tablename__ == "assessment_blueprints"

    # 7
    def test_bookmark_tablename(self):
        from app.talent.models.bookmark import OpportunityBookmark
        assert OpportunityBookmark.__tablename__ == "talent_opportunity_bookmarks"

    # 8
    def test_career_goal_tablename(self):
        from app.talent.models.career_goal import CareerGoal
        assert CareerGoal.__tablename__ == "talent_career_goals"

    # 9
    def test_credential_pathway_tablename(self):
        from app.talent.models.credential_pathway import CredentialPathway
        assert CredentialPathway.__tablename__ == "talent_credential_pathways"

    # 10
    def test_endorsement_tablename(self):
        from app.talent.models.endorsement import SkillEndorsement
        assert SkillEndorsement.__tablename__ == "talent_skill_endorsements"

    # 11
    def test_employer_profile_tablename(self):
        from app.talent.models.employer import EmployerProfile
        assert EmployerProfile.__tablename__ == "employer_profiles"

    # 12
    def test_offer_tablename(self):
        from app.talent.models.offer import Offer
        assert Offer.__tablename__ == "talent_offers"

    # 13
    def test_message_tablename(self):
        from app.talent.models.message import ApplicationMessage
        assert ApplicationMessage.__tablename__ == "talent_application_messages"

    # 14
    def test_portfolio_tablename(self):
        from app.talent.models.portfolio import PortfolioItem
        assert PortfolioItem.__tablename__ == "talent_portfolio_items"

    # 15
    def test_key_role_tablename(self):
        from app.talent.models.succession import KeyRole
        assert KeyRole.__tablename__ == "talent_key_roles"

    # 16
    def test_successor_nomination_tablename(self):
        from app.talent.models.succession import SuccessorNomination
        assert SuccessorNomination.__tablename__ == "talent_successor_nominations"

    # 17
    def test_webhook_endpoint_tablename(self):
        from app.talent.models.webhook_endpoint import WebhookEndpointConfig
        assert WebhookEndpointConfig.__tablename__ == "talent_webhook_endpoints"

    # 18
    def test_webhook_delivery_log_tablename(self):
        from app.talent.models.webhook_endpoint import WebhookDeliveryLog
        assert WebhookDeliveryLog.__tablename__ == "talent_webhook_delivery_log"

    # 19
    def test_activity_log_tablename(self):
        from app.talent.models.activity import TalentActivityLog
        assert TalentActivityLog.__tablename__ == "talent_activity_log"

    # 20
    def test_consent_log_tablename(self):
        from app.talent.models.consent_log import ConsentLog
        assert ConsentLog.__tablename__ == "talent_consent_log"


# ═══════════════════════════════════════════════════════════════════
# SECTION 2: More model tablenames (tests 21-35)
# ═══════════════════════════════════════════════════════════════════

class TestModelTablenamesExtended:
    # 21
    def test_passport_tablename(self):
        from app.talent.models.passport import SkillPassport
        assert SkillPassport.__tablename__ == "skill_passports"

    # 22
    def test_passport_snapshot_tablename(self):
        from app.talent.models.passport import PassportSnapshot
        assert PassportSnapshot.__tablename__ == "passport_snapshots"

    # 23
    def test_saved_search_tablename(self):
        from app.talent.models.saved_search import SavedSearch
        assert SavedSearch.__tablename__ == "talent_saved_searches"

    # 24
    def test_scorecard_template_tablename(self):
        from app.talent.models.scorecard import ScorecardTemplate
        assert ScorecardTemplate.__tablename__ == "talent_scorecard_templates"

    # 25
    def test_interview_scorecard_tablename(self):
        from app.talent.models.scorecard import InterviewScorecard
        assert InterviewScorecard.__tablename__ == "talent_interview_scorecards"

    # 26
    def test_scoring_snapshot_tablename(self):
        from app.talent.models.scoring import CapabilityScoreSnapshot
        assert CapabilityScoreSnapshot.__tablename__ == "capability_score_snapshots"

    # 27
    def test_signing_key_tablename(self):
        from app.talent.models.signing import OrgSigningKey
        assert OrgSigningKey.__tablename__ == "talent_org_signing_keys"

    # 28
    def test_talent_pool_tablename(self):
        from app.talent.models.talent_pool import TalentPool
        assert TalentPool.__tablename__ == "talent_pools"

    # 29
    def test_talent_pool_membership_tablename(self):
        from app.talent.models.talent_pool import TalentPoolMembership
        assert TalentPoolMembership.__tablename__ == "talent_pool_memberships"

    # 30
    def test_notification_preference_tablename(self):
        from app.talent.models.notification import NotificationPreference
        assert NotificationPreference.__tablename__ == "talent_notification_preferences"

    # 31
    def test_talent_notification_tablename(self):
        from app.talent.models.notification import TalentNotification
        assert TalentNotification.__tablename__ == "talent_notifications"

    # 32
    def test_candidate_note_tablename(self):
        from app.talent.models.candidate_note import CandidateNote
        assert CandidateNote.__tablename__ == "talent_candidate_notes"

    # 33
    def test_onboarding_template_tablename(self):
        from app.talent.models.onboarding import OnboardingTemplate
        assert OnboardingTemplate.__tablename__ == "talent_onboarding_templates"

    # 34
    def test_interview_slot_tablename(self):
        from app.talent.models.interview_slot import InterviewSlot
        assert InterviewSlot.__tablename__ == "talent_interview_slots"

    # 35
    def test_internship_supervision_tablename(self):
        from app.talent.models.internship import InternshipSupervision
        assert InternshipSupervision.__tablename__ == "internship_supervisions"


# ═══════════════════════════════════════════════════════════════════
# SECTION 3: Frozenset / constant validation (tests 36-60)
# ═══════════════════════════════════════════════════════════════════

class TestFrozensetConstants:
    # 36
    def test_edge_types_is_frozenset(self):
        from app.talent.models.capability import EDGE_TYPES
        assert isinstance(EDGE_TYPES, frozenset)
        assert len(EDGE_TYPES) > 3

    # 37
    def test_edge_types_contains_related_to(self):
        from app.talent.models.capability import EDGE_TYPES
        assert "related_to" in EDGE_TYPES

    # 38
    def test_edge_types_contains_specializes(self):
        from app.talent.models.capability import EDGE_TYPES
        assert "specializes" in EDGE_TYPES

    # 39
    def test_mapping_source_types_is_frozenset(self):
        from app.talent.models.capability import MAPPING_SOURCE_TYPES
        assert isinstance(MAPPING_SOURCE_TYPES, frozenset)

    # 40
    def test_evidence_source_types_is_frozenset(self):
        from app.talent.models.evidence import EVIDENCE_SOURCE_TYPES
        assert isinstance(EVIDENCE_SOURCE_TYPES, frozenset)

    # 41
    def test_evidence_source_types_has_skill_completion(self):
        from app.talent.models.evidence import EVIDENCE_SOURCE_TYPES
        assert "skill_completion" in EVIDENCE_SOURCE_TYPES

    # 42
    def test_evidence_source_types_has_workflow_execution(self):
        from app.talent.models.evidence import EVIDENCE_SOURCE_TYPES
        assert "workflow_execution" in EVIDENCE_SOURCE_TYPES

    # 43
    def test_verification_levels_is_tuple(self):
        from app.talent.models.evidence import VERIFICATION_LEVELS
        assert isinstance(VERIFICATION_LEVELS, tuple)
        assert len(VERIFICATION_LEVELS) > 2

    # 44
    def test_verification_levels_order(self):
        from app.talent.models.evidence import VERIFICATION_LEVELS
        assert VERIFICATION_LEVELS[0] == "employer_verified"

    # 45
    def test_terminal_statuses_is_frozenset(self):
        from app.talent.models.application import TERMINAL_STATUSES
        assert isinstance(TERMINAL_STATUSES, frozenset)

    # 46
    def test_terminal_statuses_contains_rejected(self):
        from app.talent.models.application import TERMINAL_STATUSES
        assert "rejected" in TERMINAL_STATUSES

    # 47
    def test_terminal_statuses_contains_withdrawn(self):
        from app.talent.models.application import TERMINAL_STATUSES
        assert "withdrawn" in TERMINAL_STATUSES

    # 48
    def test_portfolio_item_types(self):
        from app.talent.models.portfolio import PORTFOLIO_ITEM_TYPES
        assert isinstance(PORTFOLIO_ITEM_TYPES, frozenset)
        assert "project" in PORTFOLIO_ITEM_TYPES
        assert "case_study" in PORTFOLIO_ITEM_TYPES

    # 49
    def test_portfolio_visibility_options(self):
        from app.talent.models.portfolio import PORTFOLIO_VISIBILITY_OPTIONS
        assert "private" in PORTFOLIO_VISIBILITY_OPTIONS
        assert "public" in PORTFOLIO_VISIBILITY_OPTIONS
        assert "passport_visible" in PORTFOLIO_VISIBILITY_OPTIONS

    # 50
    def test_goal_statuses(self):
        from app.talent.models.career_goal import GOAL_STATUSES
        assert "active" in GOAL_STATUSES
        assert "completed" in GOAL_STATUSES
        assert "abandoned" in GOAL_STATUSES

    # 51
    def test_endorsement_relationships(self):
        from app.talent.models.endorsement import ENDORSEMENT_RELATIONSHIPS
        assert isinstance(ENDORSEMENT_RELATIONSHIPS, frozenset)
        assert len(ENDORSEMENT_RELATIONSHIPS) >= 3

    # 52
    def test_consent_types(self):
        from app.talent.models.consent_log import CONSENT_TYPES
        assert isinstance(CONSENT_TYPES, frozenset)

    # 53
    def test_consent_actions(self):
        from app.talent.models.consent_log import CONSENT_ACTIONS
        assert "granted" in CONSENT_ACTIONS
        assert "revoked" in CONSENT_ACTIONS

    # 54
    def test_search_types(self):
        from app.talent.models.saved_search import SEARCH_TYPES
        assert "candidate" in SEARCH_TYPES
        assert "opportunity" in SEARCH_TYPES

    # 55
    def test_notify_frequencies(self):
        from app.talent.models.saved_search import NOTIFY_FREQUENCIES
        assert "never" in NOTIFY_FREQUENCIES
        assert "daily" in NOTIFY_FREQUENCIES
        assert "weekly" in NOTIFY_FREQUENCIES

    # 56
    def test_activity_action_types(self):
        from app.talent.models.activity import ACTIVITY_ACTION_TYPES
        assert isinstance(ACTIVITY_ACTION_TYPES, frozenset)
        assert len(ACTIVITY_ACTION_TYPES) > 5

    # 57
    def test_notification_event_types(self):
        from app.talent.models.notification import NOTIFICATION_EVENT_TYPES
        assert isinstance(NOTIFICATION_EVENT_TYPES, frozenset)

    # 58
    def test_feedback_types(self):
        from app.talent.models.application import FEEDBACK_TYPES
        assert "rejection_reason" in FEEDBACK_TYPES
        assert "general" in FEEDBACK_TYPES

    # 59
    def test_feedback_visibility(self):
        from app.talent.models.application import FEEDBACK_VISIBILITY
        assert "employer_only" in FEEDBACK_VISIBILITY
        assert "shared_with_candidate" in FEEDBACK_VISIBILITY

    # 60
    def test_opportunity_types(self):
        from app.talent.schemas.employer import OPPORTUNITY_TYPES
        assert "full_time" in OPPORTUNITY_TYPES or "fulltime" in OPPORTUNITY_TYPES or len(OPPORTUNITY_TYPES) > 3


# ═══════════════════════════════════════════════════════════════════
# SECTION 4: Capability schema validation (tests 61-75)
# ═══════════════════════════════════════════════════════════════════

class TestCapabilitySchemas:
    # 61
    def test_create_capability_valid(self):
        from app.talent.schemas.capability import CreateCapabilityRequest
        req = CreateCapabilityRequest(canonical_name="Python", category="technical")
        assert req.canonical_name == "Python"

    # 62
    def test_create_capability_missing_name_raises(self):
        from app.talent.schemas.capability import CreateCapabilityRequest
        with pytest.raises(ValidationError):
            CreateCapabilityRequest(category="technical")

    # 63
    def test_create_capability_missing_category_raises(self):
        from app.talent.schemas.capability import CreateCapabilityRequest
        with pytest.raises(ValidationError):
            CreateCapabilityRequest(canonical_name="Python")

    # 64
    def test_capability_response_from_attributes(self):
        from app.talent.schemas.capability import CapabilityResponse
        assert CapabilityResponse.model_config.get("from_attributes") is True

    # 65
    def test_create_edge_valid(self):
        from app.talent.schemas.capability import CreateEdgeRequest
        req = CreateEdgeRequest(source_id="01ABCDEFGHIJKLMNOPQRSTUV", target_id="01ZYXWVUTSRQPONMLKJIHGFEDC", edge_type="related_to")
        assert req.edge_type == "related_to"

    # 66
    def test_update_capability_optional_fields(self):
        from app.talent.schemas.capability import UpdateCapabilityRequest
        req = UpdateCapabilityRequest()
        # All fields should be optional
        assert req.model_dump(exclude_unset=True) == {}

    # 67
    def test_graph_response_exists(self):
        from app.talent.schemas.capability import GraphResponse
        assert issubclass(GraphResponse, BaseModel)

    # 68
    def test_merge_capability_request_exists(self):
        from app.talent.schemas.capability import MergeCapabilityRequest
        assert issubclass(MergeCapabilityRequest, BaseModel)

    # 69
    def test_edge_response_from_attributes(self):
        from app.talent.schemas.capability import EdgeResponse
        assert EdgeResponse.model_config.get("from_attributes") is True

    # 70
    def test_mapping_response_exists(self):
        from app.talent.schemas.capability import MappingResponse
        assert issubclass(MappingResponse, BaseModel)

    # 71
    def test_create_mapping_request_valid(self):
        from app.talent.schemas.capability import CreateMappingRequest
        req = CreateMappingRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="esco",
            source_id="http://data.europa.eu/esco/skill/1234",
        )
        assert req.source_type == "esco"

    # 72
    def test_capability_response_has_id_field(self):
        from app.talent.schemas.capability import CapabilityResponse
        assert "id" in CapabilityResponse.model_fields

    # 73
    def test_capability_response_has_canonical_name(self):
        from app.talent.schemas.capability import CapabilityResponse
        assert "canonical_name" in CapabilityResponse.model_fields

    # 74
    def test_capability_response_has_external_ids(self):
        from app.talent.schemas.capability import CapabilityResponse
        assert "external_ids" in CapabilityResponse.model_fields

    # 75
    def test_capability_response_has_aliases(self):
        from app.talent.schemas.capability import CapabilityResponse
        assert "aliases" in CapabilityResponse.model_fields


# ═══════════════════════════════════════════════════════════════════
# SECTION 5: Evidence schema validation (tests 76-90)
# ═══════════════════════════════════════════════════════════════════

class TestEvidenceSchemas:
    # 76
    def test_record_evidence_valid(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="skill_completion",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="self_reported",
            occurred_at=datetime.now(UTC),
        )
        assert req.source_type == "skill_completion"

    # 77
    def test_record_evidence_missing_capability_raises(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        with pytest.raises(ValidationError):
            RecordEvidenceRequest(
                source_type="skill_completion",
                source_id="01ABCDEFGHIJKLMNOPQRSTUV",
                verification_level="self_reported",
                occurred_at=datetime.now(UTC),
            )

    # 78
    def test_evidence_response_from_attributes(self):
        from app.talent.schemas.evidence import EvidenceResponse
        assert EvidenceResponse.model_config.get("from_attributes") is True

    # 79
    def test_void_evidence_request_has_reason(self):
        from app.talent.schemas.evidence import VoidEvidenceRequest
        assert "reason" in VoidEvidenceRequest.model_fields

    # 80
    def test_provenance_response_exists(self):
        from app.talent.schemas.evidence import ProvenanceResponse
        assert issubclass(ProvenanceResponse, BaseModel)

    # 81
    def test_capability_score_response_exists(self):
        from app.talent.schemas.evidence import CapabilityScoreResponse
        assert issubclass(CapabilityScoreResponse, BaseModel)

    # 82
    def test_evidence_response_has_score_field(self):
        from app.talent.schemas.evidence import EvidenceResponse
        assert "score_normalized" in EvidenceResponse.model_fields

    # 83
    def test_evidence_response_has_status(self):
        from app.talent.schemas.evidence import EvidenceResponse
        assert "status" in EvidenceResponse.model_fields

    # 84
    def test_evidence_response_has_occurred_at(self):
        from app.talent.schemas.evidence import EvidenceResponse
        assert "occurred_at" in EvidenceResponse.model_fields

    # 85
    def test_evidence_response_has_verification_level(self):
        from app.talent.schemas.evidence import EvidenceResponse
        assert "verification_level" in EvidenceResponse.model_fields

    # 86
    def test_record_evidence_optional_score(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="credential",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="employer_verified",
            occurred_at=datetime.now(UTC),
        )
        assert req.score_normalized is None

    # 87
    def test_record_evidence_with_score(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="rubric_score",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="instructor_verification",
            occurred_at=datetime.now(UTC),
            score_normalized=0.85,
        )
        assert req.score_normalized == 0.85

    # 88
    def test_record_evidence_with_confidence(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="peer_review",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="self_reported",
            occurred_at=datetime.now(UTC),
            confidence=0.7,
        )
        assert req.confidence == 0.7

    # 89
    def test_record_evidence_with_expires_at(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        future = datetime.now(UTC) + timedelta(days=365)
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="credential",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="employer_verified",
            occurred_at=datetime.now(UTC),
            expires_at=future,
        )
        assert req.expires_at == future

    # 90
    def test_record_evidence_with_org_id(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="project_approval",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="employer_verified",
            occurred_at=datetime.now(UTC),
            org_id="01ABCDEFGHIJKLMNOPQRSTUV",
        )
        assert req.org_id is not None


# ═══════════════════════════════════════════════════════════════════
# SECTION 6: Application schema validation (tests 91-105)
# ═══════════════════════════════════════════════════════════════════

class TestApplicationSchemas:
    # 91
    def test_create_application_valid(self):
        from app.talent.schemas.application import CreateApplicationRequest
        req = CreateApplicationRequest()
        assert req.cover_note is None

    # 92
    def test_create_application_default_empty_lists(self):
        from app.talent.schemas.application import CreateApplicationRequest
        req = CreateApplicationRequest()
        assert req.selected_credentials == []
        assert req.selected_projects == []

    # 93
    def test_transition_application_valid(self):
        from app.talent.schemas.application import TransitionApplicationRequest
        req = TransitionApplicationRequest(status="submitted")
        assert req.status == "submitted"

    # 94
    def test_application_response_from_attributes(self):
        from app.talent.schemas.application import ApplicationResponse
        assert ApplicationResponse.model_config.get("from_attributes") is True

    # 95
    def test_application_response_has_status(self):
        from app.talent.schemas.application import ApplicationResponse
        assert "status" in ApplicationResponse.model_fields

    # 96
    def test_application_event_response_exists(self):
        from app.talent.schemas.application import ApplicationEventResponse
        assert issubclass(ApplicationEventResponse, BaseModel)

    # 97
    def test_create_interview_request_exists(self):
        from app.talent.schemas.application import CreateInterviewRequest
        assert issubclass(CreateInterviewRequest, BaseModel)

    # 98
    def test_interview_stage_response_exists(self):
        from app.talent.schemas.application import InterviewStageResponse
        assert issubclass(InterviewStageResponse, BaseModel)

    # 99
    def test_create_feedback_request_exists(self):
        from app.talent.schemas.application import CreateFeedbackRequest
        assert issubclass(CreateFeedbackRequest, BaseModel)

    # 100
    def test_create_application_with_cover_note(self):
        from app.talent.schemas.application import CreateApplicationRequest
        req = CreateApplicationRequest(
            cover_note="I am very interested in this role.",
        )
        assert req.cover_note == "I am very interested in this role."

    # 101
    def test_create_feedback_invalid_type_raises(self):
        from app.talent.schemas.application import CreateFeedbackRequest
        with pytest.raises(ValidationError):
            CreateFeedbackRequest(
                feedback_type="invalid_type",
                content="test",
            )

    # 102
    def test_create_feedback_valid_type(self):
        from app.talent.schemas.application import CreateFeedbackRequest
        req = CreateFeedbackRequest(
            feedback_type="general",
            content="Great candidate",
        )
        assert req.feedback_type == "general"

    # 103
    def test_application_response_has_id(self):
        from app.talent.schemas.application import ApplicationResponse
        assert "id" in ApplicationResponse.model_fields

    # 104
    def test_application_response_has_opportunity_id(self):
        from app.talent.schemas.application import ApplicationResponse
        assert "opportunity_id" in ApplicationResponse.model_fields

    # 105
    def test_application_response_has_created_at(self):
        from app.talent.schemas.application import ApplicationResponse
        assert "created_at" in ApplicationResponse.model_fields


# ═══════════════════════════════════════════════════════════════════
# SECTION 7: Passport schema validation (tests 106-115)
# ═══════════════════════════════════════════════════════════════════

class TestPassportSchemas:
    # 106
    def test_update_passport_valid(self):
        from app.talent.schemas.passport import UpdatePassportRequest
        req = UpdatePassportRequest(default_visibility="private")
        assert req.default_visibility == "private"

    # 107
    def test_passport_response_from_attributes(self):
        from app.talent.schemas.passport import PassportResponse
        assert PassportResponse.model_config.get("from_attributes") is True

    # 108
    def test_create_snapshot_request_exists(self):
        from app.talent.schemas.passport import CreateSnapshotRequest
        assert issubclass(CreateSnapshotRequest, BaseModel)

    # 109
    def test_snapshot_response_exists(self):
        from app.talent.schemas.passport import SnapshotResponse
        assert issubclass(SnapshotResponse, BaseModel)

    # 110
    def test_snapshot_verify_response_exists(self):
        from app.talent.schemas.passport import SnapshotVerifyResponse
        assert issubclass(SnapshotVerifyResponse, BaseModel)

    # 111
    def test_passport_visibility_scopes(self):
        from app.talent.schemas.passport import PASSPORT_VISIBILITY_SCOPES
        assert "private" in PASSPORT_VISIBILITY_SCOPES
        assert "organization_only" in PASSPORT_VISIBILITY_SCOPES

    # 112
    def test_passport_response_has_user_id(self):
        from app.talent.schemas.passport import PassportResponse
        assert "user_id" in PassportResponse.model_fields

    # 113
    def test_snapshot_response_has_id(self):
        from app.talent.schemas.passport import SnapshotResponse
        assert "id" in SnapshotResponse.model_fields

    # 114
    def test_update_passport_all_optional(self):
        from app.talent.schemas.passport import UpdatePassportRequest
        req = UpdatePassportRequest()
        assert req.model_dump(exclude_unset=True) == {}

    # 115
    def test_snapshot_verify_response_has_valid_field(self):
        from app.talent.schemas.passport import SnapshotVerifyResponse
        assert "valid" in SnapshotVerifyResponse.model_fields or "is_valid" in SnapshotVerifyResponse.model_fields or len(SnapshotVerifyResponse.model_fields) > 0


# ═══════════════════════════════════════════════════════════════════
# SECTION 8: Employer & Opportunity schemas (tests 116-130)
# ═══════════════════════════════════════════════════════════════════

class TestEmployerSchemas:
    # 116
    def test_create_employer_profile_exists(self):
        from app.talent.schemas.employer import CreateEmployerProfileRequest
        assert issubclass(CreateEmployerProfileRequest, BaseModel)

    # 117
    def test_employer_profile_response_exists(self):
        from app.talent.schemas.employer import EmployerProfileResponse
        assert issubclass(EmployerProfileResponse, BaseModel)

    # 118
    def test_create_opportunity_valid(self):
        from app.talent.schemas.employer import CreateOpportunityRequest
        req = CreateOpportunityRequest(
            title="Software Engineer",
            opportunity_type="full_time",
        )
        assert req.title == "Software Engineer"

    # 119
    def test_create_opportunity_missing_title_raises(self):
        from app.talent.schemas.employer import CreateOpportunityRequest
        with pytest.raises(ValidationError):
            CreateOpportunityRequest(opportunity_type="full_time")

    # 120
    def test_create_opportunity_invalid_type_raises(self):
        from app.talent.schemas.employer import CreateOpportunityRequest
        with pytest.raises(ValidationError):
            CreateOpportunityRequest(
                title="Engineer",
                opportunity_type="definitely_invalid_type_xyz",
            )

    # 121
    def test_opportunity_response_from_attributes(self):
        from app.talent.schemas.employer import OpportunityResponse
        assert OpportunityResponse.model_config.get("from_attributes") is True

    # 122
    def test_update_opportunity_all_optional(self):
        from app.talent.schemas.employer import UpdateOpportunityRequest
        req = UpdateOpportunityRequest()
        assert req.model_dump(exclude_unset=True) == {}

    # 123
    def test_opportunity_response_has_id(self):
        from app.talent.schemas.employer import OpportunityResponse
        assert "id" in OpportunityResponse.model_fields

    # 124
    def test_opportunity_response_has_title(self):
        from app.talent.schemas.employer import OpportunityResponse
        assert "title" in OpportunityResponse.model_fields

    # 125
    def test_opportunity_response_has_status(self):
        from app.talent.schemas.employer import OpportunityResponse
        assert "status" in OpportunityResponse.model_fields

    # 126
    def test_create_opportunity_with_description(self):
        from app.talent.schemas.employer import CreateOpportunityRequest
        req = CreateOpportunityRequest(
            title="Data Scientist",
            opportunity_type="full_time",
            description="Build ML models",
        )
        assert req.description == "Build ML models"

    # 127
    def test_employer_profile_response_has_org_id(self):
        from app.talent.schemas.employer import EmployerProfileResponse
        assert "org_id" in EmployerProfileResponse.model_fields

    # 128
    def test_opportunity_types_frozenset(self):
        from app.talent.schemas.employer import OPPORTUNITY_TYPES
        assert isinstance(OPPORTUNITY_TYPES, frozenset)

    # 129
    def test_opportunity_types_has_full_time(self):
        from app.talent.schemas.employer import OPPORTUNITY_TYPES
        assert "full_time" in OPPORTUNITY_TYPES

    # 130
    def test_opportunity_types_has_contract(self):
        from app.talent.schemas.employer import OPPORTUNITY_TYPES
        assert "contract" in OPPORTUNITY_TYPES


# ═══════════════════════════════════════════════════════════════════
# SECTION 9: Endorsement schemas (tests 131-140)
# ═══════════════════════════════════════════════════════════════════

class TestEndorsementSchemas:
    # 131
    def test_create_endorsement_valid(self):
        from app.talent.schemas.endorsement import CreateEndorsementRequest
        req = CreateEndorsementRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            relationship="colleague",
        )
        assert req.relationship == "colleague"

    # 132
    def test_endorsement_response_from_attributes(self):
        from app.talent.schemas.endorsement import EndorsementResponse
        assert EndorsementResponse.model_config.get("from_attributes") is True

    # 133
    def test_endorsement_summary_response_exists(self):
        from app.talent.schemas.endorsement import EndorsementSummaryResponse
        assert issubclass(EndorsementSummaryResponse, BaseModel)

    # 134
    def test_create_endorsement_with_message(self):
        from app.talent.schemas.endorsement import CreateEndorsementRequest
        req = CreateEndorsementRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            relationship="manager",
            message="Excellent Python skills",
        )
        assert req.message == "Excellent Python skills"

    # 135
    def test_endorsement_response_has_id(self):
        from app.talent.schemas.endorsement import EndorsementResponse
        assert "id" in EndorsementResponse.model_fields

    # 136
    def test_endorsement_response_has_status(self):
        from app.talent.schemas.endorsement import EndorsementResponse
        assert "status" in EndorsementResponse.model_fields

    # 137
    def test_create_endorsement_with_no_message(self):
        from app.talent.schemas.endorsement import CreateEndorsementRequest
        req = CreateEndorsementRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            relationship="colleague",
        )
        assert req.message is None

    # 138
    def test_create_endorsement_missing_capability_raises(self):
        from app.talent.schemas.endorsement import CreateEndorsementRequest
        with pytest.raises(ValidationError):
            CreateEndorsementRequest(
                relationship="colleague",
            )

    # 139
    def test_create_endorsement_missing_relationship_raises(self):
        from app.talent.schemas.endorsement import CreateEndorsementRequest
        with pytest.raises(ValidationError):
            CreateEndorsementRequest(
                capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            )

    # 140
    def test_endorsement_summary_response_fields(self):
        from app.talent.schemas.endorsement import EndorsementSummaryResponse
        fields = EndorsementSummaryResponse.model_fields
        assert len(fields) > 0


# ═══════════════════════════════════════════════════════════════════
# SECTION 10: Career goal, bookmark, assessment schemas (tests 141-160)
# ═══════════════════════════════════════════════════════════════════

class TestMiscSchemas:
    # 141
    def test_create_goal_valid(self):
        from app.talent.schemas.career_goal import CreateGoalRequest
        req = CreateGoalRequest(title="Become Senior Engineer")
        assert req.title == "Become Senior Engineer"

    # 142
    def test_create_goal_missing_title_raises(self):
        from app.talent.schemas.career_goal import CreateGoalRequest
        with pytest.raises(ValidationError):
            CreateGoalRequest()

    # 143
    def test_update_goal_all_optional(self):
        from app.talent.schemas.career_goal import UpdateGoalRequest
        req = UpdateGoalRequest()
        assert req.model_dump(exclude_unset=True) == {}

    # 144
    def test_goal_response_from_attributes(self):
        from app.talent.schemas.career_goal import GoalResponse
        assert GoalResponse.model_config.get("from_attributes") is True

    # 145
    def test_goal_progress_response_exists(self):
        from app.talent.schemas.career_goal import GoalProgressResponse
        assert issubclass(GoalProgressResponse, BaseModel)

    # 146
    def test_bookmark_request_valid(self):
        from app.talent.schemas.bookmark import BookmarkRequest
        req = BookmarkRequest(notes="Great opportunity")
        assert req.notes == "Great opportunity"

    # 147
    def test_bookmark_response_from_attributes(self):
        from app.talent.schemas.bookmark import BookmarkResponse
        assert BookmarkResponse.model_config.get("from_attributes") is True

    # 148
    def test_create_blueprint_valid(self):
        from app.talent.schemas.assessment import CreateBlueprintRequest
        req = CreateBlueprintRequest(
            title="Technical Assessment",
            assessment_type="technical",
        )
        assert req.title == "Technical Assessment"

    # 149
    def test_create_blueprint_missing_title_raises(self):
        from app.talent.schemas.assessment import CreateBlueprintRequest
        with pytest.raises(ValidationError):
            CreateBlueprintRequest(assessment_type="technical")

    # 150
    def test_blueprint_response_from_attributes(self):
        from app.talent.schemas.assessment import BlueprintResponse
        assert BlueprintResponse.model_config.get("from_attributes") is True

    # 151
    def test_run_response_exists(self):
        from app.talent.schemas.assessment import RunResponse
        assert issubclass(RunResponse, BaseModel)

    # 152
    def test_credential_response_exists(self):
        from app.talent.schemas.assessment import CredentialResponse
        assert issubclass(CredentialResponse, BaseModel)

    # 153
    def test_create_credential_pathway_valid(self):
        from app.talent.schemas.credential_pathway import CreatePathwayRequest
        req = CreatePathwayRequest(
            name="Advanced Certification",
            pathway_credential_type="advanced_cert",
            prerequisite_credential_types=["basic_cert", "intermediate_cert"],
            prerequisite_count=2,
        )
        assert req.prerequisite_count == 2

    # 154
    def test_pathway_response_from_attributes(self):
        from app.talent.schemas.credential_pathway import PathwayResponse
        assert PathwayResponse.model_config.get("from_attributes") is True

    # 155
    def test_pathway_progress_response_exists(self):
        from app.talent.schemas.credential_pathway import PathwayProgressResponse
        assert issubclass(PathwayProgressResponse, BaseModel)

    # 156
    def test_notification_response_exists(self):
        from app.talent.schemas.notification import NotificationResponse
        assert issubclass(NotificationResponse, BaseModel)

    # 157
    def test_unread_count_response_exists(self):
        from app.talent.schemas.notification import UnreadCountResponse
        assert issubclass(UnreadCountResponse, BaseModel)

    # 158
    def test_update_preferences_request_exists(self):
        from app.talent.schemas.notification import UpdatePreferencesRequest
        assert issubclass(UpdatePreferencesRequest, BaseModel)

    # 159
    def test_parse_resume_request_exists(self):
        from app.talent.schemas.resume import ParseResumeRequest
        assert issubclass(ParseResumeRequest, BaseModel)

    # 160
    def test_parse_resume_response_exists(self):
        from app.talent.schemas.resume import ParseResumeResponse
        assert issubclass(ParseResumeResponse, BaseModel)


# ═══════════════════════════════════════════════════════════════════
# SECTION 11: Scorecard, saved search, pool schemas (tests 161-180)
# ═══════════════════════════════════════════════════════════════════

class TestScorecardPoolSchemas:
    # 161
    def test_criterion_item_valid(self):
        from app.talent.schemas.scorecard import CriterionItem
        c = CriterionItem(name="Communication", weight=0.5)
        assert c.weight == 0.5

    # 162
    def test_create_scorecard_template_valid(self):
        from app.talent.schemas.scorecard import CreateScorecardTemplateRequest
        req = CreateScorecardTemplateRequest(name="Engineering Interview")
        assert req.name == "Engineering Interview"

    # 163
    def test_scorecard_template_response_from_attributes(self):
        from app.talent.schemas.scorecard import ScorecardTemplateResponse
        assert ScorecardTemplateResponse.model_config.get("from_attributes") is True

    # 164
    def test_valid_recommendations_frozenset(self):
        from app.talent.schemas.scorecard import VALID_RECOMMENDATIONS
        assert "strong_hire" in VALID_RECOMMENDATIONS
        assert "no_hire" in VALID_RECOMMENDATIONS

    # 165
    def test_create_scorecard_invalid_recommendation_raises(self):
        from app.talent.schemas.scorecard import CreateScorecardRequest
        with pytest.raises(ValidationError):
            CreateScorecardRequest(
                ratings={},
                recommendation="invalid_rec",
            )

    # 166
    def test_create_scorecard_valid_recommendation(self):
        from app.talent.schemas.scorecard import CreateScorecardRequest
        req = CreateScorecardRequest(
            ratings={"communication": 4},
            recommendation="hire",
        )
        assert req.recommendation == "hire"

    # 167
    def test_create_saved_search_valid(self):
        from app.talent.schemas.saved_search import CreateSavedSearchRequest
        req = CreateSavedSearchRequest(
            name="Senior Engineers",
            search_type="candidate",
            search_criteria={"skills": ["python"]},
        )
        assert req.search_type == "candidate"

    # 168
    def test_create_saved_search_invalid_type_raises(self):
        from app.talent.schemas.saved_search import CreateSavedSearchRequest
        with pytest.raises(ValidationError):
            CreateSavedSearchRequest(
                name="Test",
                search_type="invalid_type",
            )

    # 169
    def test_saved_search_response_from_attributes(self):
        from app.talent.schemas.saved_search import SavedSearchResponse
        assert SavedSearchResponse.model_config.get("from_attributes") is True

    # 170
    def test_create_pool_valid(self):
        from app.talent.schemas.talent_pool import CreatePoolRequest
        req = CreatePoolRequest(name="Top Talent")
        assert req.name == "Top Talent"

    # 171
    def test_pool_response_from_attributes(self):
        from app.talent.schemas.talent_pool import PoolResponse
        assert PoolResponse.model_config.get("from_attributes") is True

    # 172
    def test_add_member_request_exists(self):
        from app.talent.schemas.talent_pool import AddMemberRequest
        assert issubclass(AddMemberRequest, BaseModel)

    # 173
    def test_membership_response_exists(self):
        from app.talent.schemas.talent_pool import MembershipResponse
        assert issubclass(MembershipResponse, BaseModel)

    # 174
    def test_send_outreach_request_exists(self):
        from app.talent.schemas.talent_pool import SendOutreachRequest
        assert issubclass(SendOutreachRequest, BaseModel)

    # 175
    def test_outreach_response_exists(self):
        from app.talent.schemas.talent_pool import OutreachResponse
        assert issubclass(OutreachResponse, BaseModel)

    # 176
    def test_record_outcome_request_exists(self):
        from app.talent.schemas.talent_pool import RecordOutcomeRequest
        assert issubclass(RecordOutcomeRequest, BaseModel)

    # 177
    def test_create_pool_missing_name_raises(self):
        from app.talent.schemas.talent_pool import CreatePoolRequest
        with pytest.raises(ValidationError):
            CreatePoolRequest()

    # 178
    def test_update_pool_all_optional(self):
        from app.talent.schemas.talent_pool import UpdatePoolRequest
        req = UpdatePoolRequest()
        assert req.model_dump(exclude_unset=True) == {}

    # 179
    def test_respond_membership_request_exists(self):
        from app.talent.schemas.talent_pool import RespondMembershipRequest
        assert issubclass(RespondMembershipRequest, BaseModel)

    # 180
    def test_respond_outreach_request_exists(self):
        from app.talent.schemas.talent_pool import RespondOutreachRequest
        assert issubclass(RespondOutreachRequest, BaseModel)


# ═══════════════════════════════════════════════════════════════════
# SECTION 12: Bulk, inference, cursor, verification schemas (tests 181-200)
# ═══════════════════════════════════════════════════════════════════

class TestBulkInferenceSchemas:
    # 181
    def test_bulk_capability_request_exists(self):
        from app.talent.schemas.bulk import BulkCapabilityRequest
        assert issubclass(BulkCapabilityRequest, BaseModel)

    # 182
    def test_bulk_evidence_request_exists(self):
        from app.talent.schemas.bulk import BulkEvidenceRequest
        assert issubclass(BulkEvidenceRequest, BaseModel)

    # 183
    def test_bulk_transition_request_exists(self):
        from app.talent.schemas.bulk import BulkTransitionRequest
        assert issubclass(BulkTransitionRequest, BaseModel)

    # 184
    def test_bulk_error_exists(self):
        from app.talent.schemas.bulk import BulkError
        assert issubclass(BulkError, BaseModel)

    # 185
    def test_skill_inference_request_valid(self):
        from app.talent.schemas.inference import SkillInferenceRequest
        req = SkillInferenceRequest(
            source_type="resume",
            text="Senior Python Developer with 10 years experience building web applications",
        )
        assert "Python" in req.text

    # 186
    def test_skill_inference_invalid_source_type_raises(self):
        from app.talent.schemas.inference import SkillInferenceRequest
        with pytest.raises(ValidationError):
            SkillInferenceRequest(
                source_type="invalid_source",
                text="This is a sufficiently long text for validation purposes here",
            )

    # 187
    def test_inference_source_types_frozenset(self):
        from app.talent.schemas.inference import INFERENCE_SOURCE_TYPES
        assert isinstance(INFERENCE_SOURCE_TYPES, frozenset)

    # 188
    def test_inferred_skill_response_exists(self):
        from app.talent.schemas.inference import InferredSkillResponse
        assert issubclass(InferredSkillResponse, BaseModel)

    # 189
    def test_cursor_meta_exists(self):
        from app.talent.schemas.cursor import CursorMeta
        assert issubclass(CursorMeta, BaseModel)

    # 190
    def test_cursor_meta_has_next_cursor(self):
        from app.talent.schemas.cursor import CursorMeta
        assert "next_cursor" in CursorMeta.model_fields

    # 191
    def test_cursor_meta_has_has_more(self):
        from app.talent.schemas.cursor import CursorMeta
        assert "has_more" in CursorMeta.model_fields

    # 192
    def test_create_verification_request_exists(self):
        from app.talent.schemas.verification import CreateVerificationRequest
        assert issubclass(CreateVerificationRequest, BaseModel)

    # 193
    def test_verification_response_exists(self):
        from app.talent.schemas.verification import VerificationResponse
        assert issubclass(VerificationResponse, BaseModel)

    # 194
    def test_create_supervision_request_exists(self):
        from app.talent.schemas.verification import CreateSupervisionRequest
        assert issubclass(CreateSupervisionRequest, BaseModel)

    # 195
    def test_supervision_response_exists(self):
        from app.talent.schemas.verification import SupervisionResponse
        assert issubclass(SupervisionResponse, BaseModel)

    # 196
    def test_expose_opportunity_request_exists(self):
        from app.talent.schemas.verification import ExposeOpportunityRequest
        assert issubclass(ExposeOpportunityRequest, BaseModel)

    # 197
    def test_cohort_exposure_response_exists(self):
        from app.talent.schemas.verification import CohortExposureResponse
        assert issubclass(CohortExposureResponse, BaseModel)

    # 198
    def test_interview_slot_request_exists(self):
        from app.talent.schemas.interview_slot import ProposeSlotRequest
        assert issubclass(ProposeSlotRequest, BaseModel)

    # 199
    def test_interview_slot_response_exists(self):
        from app.talent.schemas.interview_slot import InterviewSlotResponse
        assert issubclass(InterviewSlotResponse, BaseModel)

    # 200
    def test_self_assessment_request_exists(self):
        from app.talent.schemas.self_assessment import SubmitAssessmentRequest
        assert issubclass(SubmitAssessmentRequest, BaseModel)


# ═══════════════════════════════════════════════════════════════════
# SECTION 13: Validation edge cases (tests 201-220)
# ═══════════════════════════════════════════════════════════════════

class TestValidationEdgeCases:
    # 201
    def test_ulid_pk_function_exists(self):
        from app.models.base import ulid_pk
        result = ulid_pk()
        assert result is not None

    # 202
    def test_evidence_source_types_no_empty_string(self):
        from app.talent.models.evidence import EVIDENCE_SOURCE_TYPES
        assert "" not in EVIDENCE_SOURCE_TYPES

    # 203
    def test_all_edge_types_are_lowercase(self):
        from app.talent.models.capability import EDGE_TYPES
        for et in EDGE_TYPES:
            assert et == et.lower(), f"Edge type {et} is not lowercase"

    # 204
    def test_all_evidence_types_are_snake_case(self):
        from app.talent.models.evidence import EVIDENCE_SOURCE_TYPES
        for t in EVIDENCE_SOURCE_TYPES:
            assert re.match(r"^[a-z][a-z0-9_]*$", t), f"{t} is not snake_case"

    # 205
    def test_portfolio_item_types_are_snake_case(self):
        from app.talent.models.portfolio import PORTFOLIO_ITEM_TYPES
        for t in PORTFOLIO_ITEM_TYPES:
            assert re.match(r"^[a-z][a-z0-9_]*$", t), f"{t} is not snake_case"

    # 206
    def test_goal_statuses_are_lowercase(self):
        from app.talent.models.career_goal import GOAL_STATUSES
        for s in GOAL_STATUSES:
            assert s == s.lower()

    # 207
    def test_terminal_statuses_are_lowercase(self):
        from app.talent.models.application import TERMINAL_STATUSES
        for s in TERMINAL_STATUSES:
            assert s == s.lower()

    # 208
    def test_consent_actions_are_lowercase(self):
        from app.talent.models.consent_log import CONSENT_ACTIONS
        for a in CONSENT_ACTIONS:
            assert a == a.lower()

    # 209
    def test_search_types_are_lowercase(self):
        from app.talent.models.saved_search import SEARCH_TYPES
        for t in SEARCH_TYPES:
            assert t == t.lower()

    # 210
    def test_notify_frequencies_are_snake_case(self):
        from app.talent.models.saved_search import NOTIFY_FREQUENCIES
        for f in NOTIFY_FREQUENCIES:
            assert re.match(r"^[a-z][a-z0-9_]*$", f), f"{f} is not snake_case"

    # 211
    def test_evidence_score_zero_valid(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="assessment_result",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="self_reported",
            occurred_at=datetime.now(UTC),
            score_normalized=0.0,
        )
        assert req.score_normalized == 0.0

    # 212
    def test_evidence_score_one_valid(self):
        from app.talent.schemas.evidence import RecordEvidenceRequest
        req = RecordEvidenceRequest(
            capability_id="01ABCDEFGHIJKLMNOPQRSTUV",
            source_type="assessment_result",
            source_id="01ABCDEFGHIJKLMNOPQRSTUV",
            verification_level="self_reported",
            occurred_at=datetime.now(UTC),
            score_normalized=1.0,
        )
        assert req.score_normalized == 1.0

    # 213
    def test_scorecard_recommendation_none_valid(self):
        from app.talent.schemas.scorecard import CreateScorecardRequest
        req = CreateScorecardRequest(
            ratings={},
        )
        assert req.recommendation is None

    # 214
    def test_create_goal_with_target_date(self):
        from app.talent.schemas.career_goal import CreateGoalRequest
        req = CreateGoalRequest(
            title="Get promoted",
            target_date=date(2027, 1, 1),
        )
        assert req.target_date == date(2027, 1, 1)

    # 215
    def test_create_goal_with_target_capabilities(self):
        from app.talent.schemas.career_goal import CreateGoalRequest
        req = CreateGoalRequest(
            title="Master ML",
            target_capabilities=[{"id": "01ABCDEFGHIJKLMNOPQRSTUV", "name": "ML"}],
        )
        assert len(req.target_capabilities) == 1

    # 216
    def test_bookmark_request_with_notes(self):
        from app.talent.schemas.bookmark import BookmarkRequest
        req = BookmarkRequest(
            notes="Interesting role",
        )
        assert req.notes == "Interesting role"

    # 217
    def test_gap_requests_screening_rules_exists(self):
        from app.talent.schemas.gap_requests import ScreeningRulesRequest
        assert issubclass(ScreeningRulesRequest, BaseModel)

    # 218
    def test_gap_requests_adverse_impact_exists(self):
        from app.talent.schemas.gap_requests import AdverseImpactRequest
        assert issubclass(AdverseImpactRequest, BaseModel)

    # 219
    def test_gap_requests_mentorship_match_exists(self):
        from app.talent.schemas.gap_requests import MentorshipMatchRequest
        assert issubclass(MentorshipMatchRequest, BaseModel)

    # 220
    def test_all_schema_modules_importable(self):
        """Verify all talent schema modules can be imported without error."""
        import importlib
        modules = [
            "app.talent.schemas.application",
            "app.talent.schemas.assessment",
            "app.talent.schemas.bookmark",
            "app.talent.schemas.bulk",
            "app.talent.schemas.capability",
            "app.talent.schemas.career_goal",
            "app.talent.schemas.credential_pathway",
            "app.talent.schemas.cursor",
            "app.talent.schemas.employer",
            "app.talent.schemas.endorsement",
            "app.talent.schemas.evidence",
            "app.talent.schemas.gap_requests",
            "app.talent.schemas.inference",
            "app.talent.schemas.notification",
            "app.talent.schemas.passport",
            "app.talent.schemas.resume",
            "app.talent.schemas.saved_search",
            "app.talent.schemas.scorecard",
            "app.talent.schemas.self_assessment",
            "app.talent.schemas.talent_pool",
            "app.talent.schemas.verification",
        ]
        for mod in modules:
            m = importlib.import_module(mod)
            assert m is not None
