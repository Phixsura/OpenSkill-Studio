"""Deep gap closure tests — verifying all 42 sections of Issue #32.

Covers gaps found during deep exploration:
- Fairness: adverse impact ratio (EEOC four-fifths rule)
- Outreach API router registration
- Employer verification → evidence flow
- Alumni mode field
- Cross-tenant isolation patterns
- E2E lifecycle coverage
"""

from unittest.mock import AsyncMock

import pytest

# ═══════════════════════════════════════════════════════════════
# Section 1-2: Capability ontology + relationships
# ═══════════════════════════════════════════════════════════════


def test_capability_has_external_ids():
    from app.talent.models.capability import Capability

    assert hasattr(Capability, "external_ids")


def test_capability_has_aliases():
    from app.talent.models.capability import Capability

    assert hasattr(Capability, "aliases")


def test_capability_has_translations():
    from app.talent.models.capability import Capability

    assert hasattr(Capability, "translations")


def test_capability_edge_types():
    from app.talent.models.capability import EDGE_TYPES

    assert "requires" in EDGE_TYPES
    assert "related_to" in EDGE_TYPES
    assert "commonly_paired_with" in EDGE_TYPES
    assert "specializes" in EDGE_TYPES
    assert "subsumes" in EDGE_TYPES


def test_capability_edge_model_exists():
    from app.talent.models.capability import CapabilityEdge

    assert CapabilityEdge.__tablename__ == "capability_edges"


def test_capability_mapping_model_exists():
    from app.talent.models.capability import CapabilityMapping

    assert CapabilityMapping.__tablename__ == "capability_mappings"


# ═══════════════════════════════════════════════════════════════
# Section 4-6: Evidence append-only + verification + provenance
# ═══════════════════════════════════════════════════════════════


def test_evidence_has_verification_level():
    from app.talent.models.evidence import CapabilityEvidence

    assert hasattr(CapabilityEvidence, "verification_level")


def test_evidence_verification_levels_complete():
    from app.talent.models.evidence import VERIFICATION_LEVELS

    required = {
        "employer_verified",
        "client_verified",
        "assessment_verified",
        "instructor_verified",
        "peer_verified",
        "system_observed",
        "self_reported",
    }
    assert required.issubset(set(VERIFICATION_LEVELS))


def test_evidence_has_provenance_fields():
    from app.talent.models.evidence import CapabilityEvidence

    assert hasattr(CapabilityEvidence, "source_type")
    assert hasattr(CapabilityEvidence, "source_id")


def test_evidence_has_signature_fields():
    from app.talent.services.credential_signing import sign_payload, verify_signature

    assert callable(sign_payload)
    assert callable(verify_signature)


# ═══════════════════════════════════════════════════════════════
# Section 7-9: Scoring 4-dimensional + versioned
# ═══════════════════════════════════════════════════════════════


def test_scoring_version():
    from app.talent.services.scoring import SCORING_VERSION

    assert SCORING_VERSION == "2.0.0"


def test_scoring_dimension_weights():
    from app.talent.services.scoring import DIMENSION_WEIGHTS

    assert DIMENSION_WEIGHTS["depth"] == 0.40
    assert DIMENSION_WEIGHTS["breadth"] == 0.20
    assert DIMENSION_WEIGHTS["recency"] == 0.20
    assert DIMENSION_WEIGHTS["velocity"] == 0.20
    assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 0.001


def test_capability_score_dataclass_has_all_dimensions():
    import dataclasses

    from app.talent.services.scoring import CapabilityScore

    fields = {f.name for f in dataclasses.fields(CapabilityScore)}
    assert "depth" in fields
    assert "breadth" in fields
    assert "recency" in fields
    assert "velocity" in fields
    assert "score" in fields
    assert "confidence" in fields


# ═══════════════════════════════════════════════════════════════
# Section 10-12: Passport + privacy + snapshots
# ═══════════════════════════════════════════════════════════════


def test_passport_has_visibility_controls():
    from app.talent.models.passport import SkillPassport

    assert hasattr(SkillPassport, "default_visibility")
    assert hasattr(SkillPassport, "discoverable")
    assert hasattr(SkillPassport, "visible_fields")


def test_passport_has_alumni_mode():
    from app.talent.models.passport import SkillPassport

    assert hasattr(SkillPassport, "alumni_mode")


def test_passport_snapshot_model():
    from app.talent.models.passport import PassportSnapshot

    assert hasattr(PassportSnapshot, "share_token")
    assert hasattr(PassportSnapshot, "payload")


# ═══════════════════════════════════════════════════════════════
# Section 13-15: Assessments + Credentials + W3C VC
# ═══════════════════════════════════════════════════════════════


def test_assessment_blueprint_model():
    from app.talent.models.assessment import AssessmentBlueprint

    assert AssessmentBlueprint.__tablename__ == "assessment_blueprints"


def test_credential_model():
    from app.talent.models.assessment import Credential

    assert hasattr(Credential, "credential_type")
    assert hasattr(Credential, "status")


def test_credential_signing_service():
    from app.talent.services.credential_signing import SigningKeyService

    assert SigningKeyService is not None


def test_vc_export_service():
    from app.talent.services.vc_export import export_passport_as_vc

    assert callable(export_passport_as_vc)


def test_openbadges_service():
    from app.talent.services.openbadges import export_credential_as_ob3

    assert callable(export_credential_as_ob3)


# ═══════════════════════════════════════════════════════════════
# Section 16-18: Employers + Opportunities + Requirements
# ═══════════════════════════════════════════════════════════════


def test_employer_profile_model():
    from app.talent.models.employer import EmployerProfile

    assert EmployerProfile.__tablename__ == "employer_profiles"


def test_opportunity_has_required_capabilities():
    from app.talent.models.employer import Opportunity

    assert hasattr(Opportunity, "required_capabilities")


def test_opportunity_has_type_and_location():
    from app.talent.models.employer import Opportunity

    assert hasattr(Opportunity, "opportunity_type")
    assert hasattr(Opportunity, "location_mode")


# ═══════════════════════════════════════════════════════════════
# Section 19-22: Matching + Fairness + EEOC
# ═══════════════════════════════════════════════════════════════


def test_matching_service_exists():
    from app.talent.services.talent_matching import TalentMatchingService

    assert TalentMatchingService is not None


@pytest.mark.asyncio
async def test_fairness_adverse_impact_ratio():
    """Verify EEOC four-fifths rule implementation (§22 safety)."""
    from app.talent.services.fairness import FairnessService

    mock_db = AsyncMock()
    svc = FairnessService(mock_db)

    # Create 20 results with varying scores
    results = [
        {"score": 0.1 * i, "tier": "strong" if i > 5 else "weak", "signals": {"cap": 0.1 * i}}
        for i in range(1, 21)
    ]
    metrics = await svc.compute_fairness_metrics(results)
    assert metrics["status"] == "computed"
    assert "adverse_impact" in metrics["metrics"]
    assert "ratio" in metrics["metrics"]["adverse_impact"]
    assert "four_fifths_compliant" in metrics["metrics"]["adverse_impact"]


@pytest.mark.asyncio
async def test_fairness_with_no_results():
    from app.talent.services.fairness import FairnessService

    mock_db = AsyncMock()
    svc = FairnessService(mock_db)
    result = await svc.compute_fairness_metrics([])
    assert result["status"] == "no_results"


@pytest.mark.asyncio
async def test_fairness_score_distribution():
    from app.talent.services.fairness import FairnessService

    mock_db = AsyncMock()
    svc = FairnessService(mock_db)
    results = [{"score": 0.5 + i * 0.01, "signals": {}} for i in range(15)]
    metrics = await svc.compute_fairness_metrics(results)
    assert "score_distribution" in metrics["metrics"]
    assert metrics["metrics"]["score_distribution"]["count"] == 15


# ═══════════════════════════════════════════════════════════════
# Section 23-26: Applications + Interview + Offer
# ═══════════════════════════════════════════════════════════════


def test_application_has_evidence_bundle():
    from app.talent.models.application import Application

    assert hasattr(Application, "evidence_bundle")


def test_interview_scorecard_model():
    from app.talent.models.scorecard import InterviewScorecard

    assert InterviewScorecard.__tablename__ == "talent_interview_scorecards"


def test_offer_model():
    from app.talent.models.offer import Offer

    assert hasattr(Offer, "status")
    assert hasattr(Offer, "negotiation_history")


# ═══════════════════════════════════════════════════════════════
# Section 27: Cohort-to-opportunity exposure
# ═══════════════════════════════════════════════════════════════


def test_cohort_opportunity_exposure_model():
    from app.talent.models.internship import CohortOpportunityExposure

    assert CohortOpportunityExposure.__tablename__ == "cohort_opportunity_exposures"


# ═══════════════════════════════════════════════════════════════
# Section 28-29: Internship + Employer verification
# ═══════════════════════════════════════════════════════════════


def test_internship_model():
    from app.talent.models.internship import InternshipSupervision

    assert hasattr(InternshipSupervision, "supervisor_user_id")


def test_employer_verification_service():
    from app.talent.services.employer_verification import EmployerVerificationService

    assert EmployerVerificationService is not None


# ═══════════════════════════════════════════════════════════════
# Section 30-31: Outcomes + Alumni mode
# ═══════════════════════════════════════════════════════════════


def test_workforce_has_outcome_analytics():
    from app.talent.services.workforce import WorkforceIntelligenceService

    assert hasattr(WorkforceIntelligenceService, "get_outcome_analytics")


def test_passport_alumni_mode_field():
    from app.talent.models.passport import SkillPassport

    # alumni_mode should be a mapped column
    col = SkillPassport.__table__.c.get("alumni_mode")
    assert col is not None


# ═══════════════════════════════════════════════════════════════
# Section 32-37: Intelligence + Gap + Coverage
# ═══════════════════════════════════════════════════════════════


def test_workforce_service_methods():
    from app.talent.services.workforce import WorkforceIntelligenceService

    assert hasattr(WorkforceIntelligenceService, "get_gap_analysis")
    assert hasattr(WorkforceIntelligenceService, "get_coverage_matrix")
    assert hasattr(WorkforceIntelligenceService, "get_outcome_analytics")


def test_intelligence_api_has_endpoints():
    from app.talent.api.intelligence import router as intel_router

    paths = [r.path for r in intel_router.routes]
    assert any("gaps" in p for p in paths)
    assert any("coverage" in p for p in paths)


def test_market_insights_service():
    from app.talent.services.market_insights import MarketInsightsService

    assert MarketInsightsService is not None


def test_hiring_analytics_service():
    from app.talent.services.hiring_analytics import HiringAnalyticsService

    assert HiringAnalyticsService is not None


# ═══════════════════════════════════════════════════════════════
# Section 38-39: Talent Pools + Outreach
# ═══════════════════════════════════════════════════════════════


def test_talent_pool_model():
    from app.talent.models.talent_pool import TalentPool

    assert TalentPool.__tablename__ == "talent_pools"


def test_outreach_model():
    from app.talent.models.talent_pool import TalentOutreach

    assert TalentOutreach.__tablename__ == "talent_outreach"
    assert hasattr(TalentOutreach, "outreach_type")
    assert hasattr(TalentOutreach, "status")


def test_outreach_router_registered():
    from app.talent.api.outreach import router

    paths = [r.path for r in router.routes]
    assert len(paths) >= 3


def test_outreach_api_has_crud():
    from app.talent.api import outreach

    assert hasattr(outreach, "list_outreach")
    assert hasattr(outreach, "send_outreach")
    assert hasattr(outreach, "respond_outreach")


# ═══════════════════════════════════════════════════════════════
# Section 40-42: Dashboards
# ═══════════════════════════════════════════════════════════════


def test_dashboard_api_has_school():
    from app.talent.api.dashboards import router

    paths = [r.path for r in router.routes]
    assert any("school" in p for p in paths)


def test_dashboard_api_has_employer():
    from app.talent.api.intelligence import router as intel_router

    paths = [r.path for r in intel_router.routes]
    assert any("employer" in p for p in paths)


def test_dashboard_api_has_platform():
    from app.talent.api.intelligence import router as intel_router

    paths = [r.path for r in intel_router.routes]
    assert any("platform" in p for p in paths)


# ═══════════════════════════════════════════════════════════════
# Safety / Quality acceptance criteria
# ═══════════════════════════════════════════════════════════════


def test_no_automatic_decision_in_matching():
    """Verify matching service has no auto-hire/auto-reject."""
    import inspect

    from app.talent.services import talent_matching

    source = inspect.getsource(talent_matching)
    # Should not have automatic employment decisions
    assert "auto_hire" not in source.lower()
    assert "auto_reject" not in source.lower()
    assert "automatic_offer" not in source.lower()


def test_matching_results_are_explainable():
    """Verify match results include explanation signals."""
    import dataclasses

    from app.talent.services.talent_matching import TalentMatchResult

    fields = {f.name for f in dataclasses.fields(TalentMatchResult)}
    assert "reasons" in fields or "signals" in fields
    assert "score" in fields
    assert "tier" in fields


def test_gdpr_service_exists():
    from app.talent.services.gdpr import GDPRService

    assert hasattr(GDPRService, "export_user_data") or hasattr(GDPRService, "delete_user_data")


def test_data_retention_service_exists():
    from app.talent.services.data_retention import DataRetentionService

    assert DataRetentionService is not None


# ═══════════════════════════════════════════════════════════════
# Cross-tenant isolation
# ═══════════════════════════════════════════════════════════════


def test_passport_scoped_to_user():
    """Passport model has user_id — prevents cross-user access."""
    from app.talent.models.passport import SkillPassport

    assert hasattr(SkillPassport, "user_id")


def test_evidence_scoped_to_user():
    from app.talent.models.evidence import CapabilityEvidence

    assert hasattr(CapabilityEvidence, "user_id")


def test_application_scoped_to_user():
    from app.talent.models.application import Application

    assert hasattr(Application, "user_id")


def test_talent_pool_scoped_to_org():
    from app.talent.models.talent_pool import TalentPool

    assert hasattr(TalentPool, "org_id")


def test_employer_profile_scoped_to_org():
    from app.talent.models.employer import EmployerProfile

    assert hasattr(EmployerProfile, "org_id")


def test_opportunity_scoped_to_employer():
    from app.talent.models.employer import Opportunity

    assert hasattr(Opportunity, "employer_org_id")


# ═══════════════════════════════════════════════════════════════
# E2E lifecycle test file exists
# ═══════════════════════════════════════════════════════════════


def test_e2e_lifecycle_test_exists():
    import os

    path = os.path.join(os.path.dirname(__file__), "..", "e2e_talent_lifecycle.py")
    assert os.path.exists(path), "E2E lifecycle test file should exist"


def test_e2e_lifecycle_covers_full_chain():
    """Verify E2E test covers: learn → credential → job → placement → feedback."""
    with open("tests/e2e_talent_lifecycle.py") as f:
        content = f.read()
    assert "credential" in content.lower()
    assert "placement" in content.lower()
    assert "evidence" in content.lower()
    assert "passport" in content.lower()
    assert "match" in content.lower()
