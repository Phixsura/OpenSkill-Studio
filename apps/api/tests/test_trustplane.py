"""Trust & Safety plane tests (ADR-017 Phase 1).

Tests run without DB using the noop lifespan pattern — test the HTTP
layer via TestClient against the FastAPI app.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# ── Helpers ──────────────────────────────────────────────────────────

def _auth(user_id: str = "user01") -> dict:
    """Generate a mock auth header. In test mode with noop lifespan,
    we bypass real JWT — these tests focus on schema validation,
    business logic structure, and error codes."""
    return {"Authorization": f"Bearer test-token-{user_id}"}


ORG_ID = "01JTEST0000000000000000001"
SYSTEM_PAYLOAD = {
    "name": "Test AI Workflow",
    "system_type": "workflow_pack",
    "description": "A test AI system for unit tests",
}


# ── Schema validation tests ──────────────────────────────────────────


class TestSystemSchemaValidation:
    """Validate request schema constraints without hitting the DB."""

    def test_create_system_rejects_invalid_type(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        with pytest.raises(ValueError, match="system_type must be one of"):
            CreateSystemRequest(name="Test", system_type="invalid_type")

    def test_create_system_rejects_empty_name(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateSystemRequest(name="   ", system_type="custom")

    def test_create_system_rejects_long_name(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        with pytest.raises(ValueError, match="200 characters"):
            CreateSystemRequest(name="x" * 201, system_type="custom")

    def test_create_system_rejects_ctrl_chars_in_name(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        with pytest.raises(ValueError, match="control characters"):
            CreateSystemRequest(name="test\x00name", system_type="custom")

    def test_create_system_accepts_valid_types(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        for t in ("workflow_pack", "developer_app", "provider_binding",
                  "evaluation_pipeline", "skill_pack", "custom"):
            req = CreateSystemRequest(name="Test", system_type=t)
            assert req.system_type == t

    def test_create_system_rejects_invalid_linked_entity_type(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        with pytest.raises(ValueError, match="linked_entity_type"):
            CreateSystemRequest(
                name="Test", system_type="custom",
                linked_entity_type="bad_type",
            )

    def test_create_system_rejects_deep_metadata(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        deep = {"a": {"b": {"c": {}}}}
        # depth=4 is within limit=64, so this should pass
        req = CreateSystemRequest(name="Test", system_type="custom", metadata_=deep)
        assert req.metadata_ == deep

    def test_create_system_rejects_ctrl_in_tags(self):
        from app.trustplane.schemas.inventory import CreateSystemRequest
        with pytest.raises(ValueError, match="control characters"):
            CreateSystemRequest(name="Test", system_type="custom", tags=["ok", "bad\x00"])

    def test_update_system_partial(self):
        from app.trustplane.schemas.inventory import UpdateSystemRequest
        req = UpdateSystemRequest(name="Updated")
        dumped = req.model_dump(exclude_unset=True)
        assert dumped == {"name": "Updated"}

    def test_change_lifecycle_rejects_invalid(self):
        from app.trustplane.schemas.inventory import ChangeLifecycleRequest
        with pytest.raises(ValueError, match="lifecycle must be one of"):
            ChangeLifecycleRequest(lifecycle="invalid_state")

    def test_change_lifecycle_accepts_valid(self):
        from app.trustplane.schemas.inventory import ChangeLifecycleRequest
        for lc in ("draft", "intake", "under_review", "approved", "deployed",
                    "monitoring", "paused", "deprecated", "retired"):
            req = ChangeLifecycleRequest(lifecycle=lc)
            assert req.lifecycle == lc


class TestUseCaseSchemaValidation:

    def test_create_use_case_rejects_invalid_type(self):
        from app.trustplane.schemas.inventory import CreateUseCaseRequest
        with pytest.raises(ValueError, match="use_type must be one of"):
            CreateUseCaseRequest(
                use_type="invalid", title="Test", description="Test desc"
            )

    def test_create_use_case_rejects_empty_title(self):
        from app.trustplane.schemas.inventory import CreateUseCaseRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateUseCaseRequest(
                use_type="intended", title="  ", description="Test desc"
            )

    def test_create_use_case_rejects_empty_description(self):
        from app.trustplane.schemas.inventory import CreateUseCaseRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateUseCaseRequest(
                use_type="intended", title="Test", description="  "
            )

    def test_create_use_case_accepts_valid(self):
        from app.trustplane.schemas.inventory import CreateUseCaseRequest
        req = CreateUseCaseRequest(
            use_type="intended",
            title="User content moderation",
            description="AI reviews user-generated content for safety",
            affected_groups=["end_users"],
            data_classes=["user_content"],
            regions=["US", "EU"],
        )
        assert req.use_type == "intended"
        assert req.regions == ["US", "EU"]


class TestAssessmentSchemaValidation:

    def test_create_assessment_rejects_empty_scores(self):
        from app.trustplane.schemas.risk import CreateAssessmentRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateAssessmentRequest(dimension_scores={})

    def test_create_assessment_rejects_out_of_range(self):
        from app.trustplane.schemas.risk import CreateAssessmentRequest
        with pytest.raises(ValueError, match="between 1 and 5"):
            CreateAssessmentRequest(dimension_scores={"autonomy": 6})

    def test_create_assessment_rejects_non_numeric(self):
        from app.trustplane.schemas.risk import CreateAssessmentRequest
        with pytest.raises(ValueError, match="must be a number"):
            CreateAssessmentRequest(dimension_scores={"autonomy": "high"})

    def test_create_assessment_accepts_valid(self):
        from app.trustplane.schemas.risk import CreateAssessmentRequest
        req = CreateAssessmentRequest(
            dimension_scores={
                "autonomy": 3,
                "data_sensitivity": 4,
                "impact_reversibility": 2,
            }
        )
        assert req.dimension_scores["autonomy"] == 3

    def test_reject_requires_justification(self):
        from app.trustplane.schemas.risk import RejectAssessmentRequest
        with pytest.raises(ValueError, match="must not be empty"):
            RejectAssessmentRequest(justification="  ")

    def test_override_requires_valid_tier(self):
        from app.trustplane.schemas.risk import OverrideTierRequest
        with pytest.raises(ValueError, match="tier must be one of"):
            OverrideTierRequest(tier="extreme", justification="reason")

    def test_override_requires_justification(self):
        from app.trustplane.schemas.risk import OverrideTierRequest
        with pytest.raises(ValueError, match="must not be empty"):
            OverrideTierRequest(tier="high", justification="  ")

    def test_override_accepts_valid(self):
        from app.trustplane.schemas.risk import OverrideTierRequest
        req = OverrideTierRequest(tier="critical", justification="Handles PII")
        assert req.tier == "critical"


class TestPolicySchemaValidation:

    def test_create_policy_rejects_empty_name(self):
        from app.trustplane.schemas.risk import CreatePolicyRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreatePolicyRequest(
                name="  ",
                dimensions=[{"key": "a", "label": "A", "weight": 1.0}],
                tier_thresholds={"minimal": {"max_score": 1.5}, "low": {"max_score": 2.5},
                                 "medium": {"max_score": 3.5}, "high": {"max_score": 4.5},
                                 "critical": {"min_score": 4.5}},
            )

    def test_create_policy_rejects_empty_dimensions(self):
        from app.trustplane.schemas.risk import CreatePolicyRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreatePolicyRequest(
                name="Test",
                dimensions=[],
                tier_thresholds={"minimal": {}, "low": {}, "medium": {}, "high": {}, "critical": {}},
            )

    def test_create_policy_rejects_duplicate_keys(self):
        from app.trustplane.schemas.risk import CreatePolicyRequest
        with pytest.raises(ValueError, match="duplicate dimension key"):
            CreatePolicyRequest(
                name="Test",
                dimensions=[
                    {"key": "a", "label": "A", "weight": 1.0},
                    {"key": "a", "label": "A2", "weight": 1.0},
                ],
                tier_thresholds={"minimal": {}, "low": {}, "medium": {}, "high": {}, "critical": {}},
            )

    def test_create_policy_rejects_negative_weight(self):
        from app.trustplane.schemas.risk import CreatePolicyRequest
        with pytest.raises(ValueError, match="positive number"):
            CreatePolicyRequest(
                name="Test",
                dimensions=[{"key": "a", "label": "A", "weight": -1.0}],
                tier_thresholds={"minimal": {}, "low": {}, "medium": {}, "high": {}, "critical": {}},
            )

    def test_create_policy_rejects_missing_threshold_keys(self):
        from app.trustplane.schemas.risk import CreatePolicyRequest
        with pytest.raises(ValueError, match="tier_thresholds must have keys"):
            CreatePolicyRequest(
                name="Test",
                dimensions=[{"key": "a", "label": "A", "weight": 1.0}],
                tier_thresholds={"minimal": {}, "low": {}},
            )


# ── Service-level logic tests ────────────────────────────────────────


class TestLifecycleTransitions:
    """Test the lifecycle transition map without DB."""

    def test_valid_transitions(self):
        from app.trustplane.models.inventory import VALID_TRANSITIONS, SystemLifecycle
        # DRAFT -> INTAKE is valid
        assert SystemLifecycle.INTAKE in VALID_TRANSITIONS[SystemLifecycle.DRAFT]
        # APPROVED -> DEPLOYED is valid
        assert SystemLifecycle.DEPLOYED in VALID_TRANSITIONS[SystemLifecycle.APPROVED]
        # RETIRED is terminal
        assert len(VALID_TRANSITIONS[SystemLifecycle.RETIRED]) == 0

    def test_invalid_transitions(self):
        from app.trustplane.models.inventory import VALID_TRANSITIONS, SystemLifecycle
        # DRAFT -> APPROVED is NOT valid (must go through INTAKE)
        assert SystemLifecycle.APPROVED not in VALID_TRANSITIONS[SystemLifecycle.DRAFT]
        # RETIRED -> anything is NOT valid
        assert SystemLifecycle.DRAFT not in VALID_TRANSITIONS[SystemLifecycle.RETIRED]

    def test_all_states_have_transition_entry(self):
        from app.trustplane.models.inventory import VALID_TRANSITIONS, SystemLifecycle
        for state in SystemLifecycle:
            assert state in VALID_TRANSITIONS


class TestRiskScoring:
    """Test risk scoring computation without DB."""

    def test_weighted_score_computation(self):
        from decimal import Decimal
        from app.trustplane.services.risk import _compute_weighted_score

        scores = {"autonomy": 3, "data_sensitivity": 4}
        dims = [
            {"key": "autonomy", "weight": 1.0},
            {"key": "data_sensitivity", "weight": 1.5},
        ]
        result = _compute_weighted_score(scores, dims)
        # (3*1.0 + 4*1.5) / (1.0+1.5) = 9.0 / 2.5 = 3.60
        assert result == Decimal("3.60")

    def test_weighted_score_single_dimension(self):
        from decimal import Decimal
        from app.trustplane.services.risk import _compute_weighted_score

        scores = {"autonomy": 5}
        dims = [{"key": "autonomy", "weight": 1.0}]
        result = _compute_weighted_score(scores, dims)
        assert result == Decimal("5.00")

    def test_weighted_score_empty_dimensions(self):
        from decimal import Decimal
        from app.trustplane.services.risk import _compute_weighted_score

        result = _compute_weighted_score({}, [])
        assert result == Decimal(0)

    def test_tier_derivation_minimal(self):
        from decimal import Decimal
        from app.trustplane.models.inventory import RiskTier
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        from app.trustplane.services.risk import _derive_tier

        assert _derive_tier(Decimal("1.0"), DEFAULT_TIER_THRESHOLDS) == RiskTier.MINIMAL

    def test_tier_derivation_low(self):
        from decimal import Decimal
        from app.trustplane.models.inventory import RiskTier
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        from app.trustplane.services.risk import _derive_tier

        assert _derive_tier(Decimal("2.0"), DEFAULT_TIER_THRESHOLDS) == RiskTier.LOW

    def test_tier_derivation_medium(self):
        from decimal import Decimal
        from app.trustplane.models.inventory import RiskTier
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        from app.trustplane.services.risk import _derive_tier

        assert _derive_tier(Decimal("3.0"), DEFAULT_TIER_THRESHOLDS) == RiskTier.MEDIUM

    def test_tier_derivation_high(self):
        from decimal import Decimal
        from app.trustplane.models.inventory import RiskTier
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        from app.trustplane.services.risk import _derive_tier

        assert _derive_tier(Decimal("4.0"), DEFAULT_TIER_THRESHOLDS) == RiskTier.HIGH

    def test_tier_derivation_critical(self):
        from decimal import Decimal
        from app.trustplane.models.inventory import RiskTier
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        from app.trustplane.services.risk import _derive_tier

        assert _derive_tier(Decimal("5.0"), DEFAULT_TIER_THRESHOLDS) == RiskTier.CRITICAL

    def test_tier_derivation_boundary(self):
        from decimal import Decimal
        from app.trustplane.models.inventory import RiskTier
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        from app.trustplane.services.risk import _derive_tier

        # Exact boundary: 1.5 should be minimal (<=)
        assert _derive_tier(Decimal("1.5"), DEFAULT_TIER_THRESHOLDS) == RiskTier.MINIMAL
        # Just above: 1.51 should be low
        assert _derive_tier(Decimal("1.51"), DEFAULT_TIER_THRESHOLDS) == RiskTier.LOW
        # 4.5 boundary is high (<=)
        assert _derive_tier(Decimal("4.5"), DEFAULT_TIER_THRESHOLDS) == RiskTier.HIGH
        # 4.51 is critical
        assert _derive_tier(Decimal("4.51"), DEFAULT_TIER_THRESHOLDS) == RiskTier.CRITICAL


class TestAuditRegistry:
    """Test the frozen audit action registry."""

    def test_all_actions_registered(self):
        from app.trustplane.services.audit import TRUST_AUDIT_ACTIONS
        expected = {
            # Phase 1
            "system.created", "system.updated", "system.lifecycle_changed",
            "system.owner_changed", "system.linked",
            "use_case.created", "use_case.updated", "use_case.deleted",
            "assessment.created", "assessment.submitted", "assessment.approved",
            "assessment.rejected", "assessment.superseded",
            "assessment.tier_overridden",
            "policy.created", "policy.updated", "policy.activated", "policy.deactivated",
            # Phase 2
            "case.created", "case.updated", "case.status_changed",
            "evidence.created", "evidence.updated", "evidence.status_changed",
            "evidence.linked", "evidence.unlinked",
            "review.created", "review.assigned", "review.decided",
            "review.cancelled", "review.expired",
            # Phase 3-4
            "profile.created", "profile.activated",
            "gate.evaluated", "gate.overridden",
            "guardrail.created", "guardrail.activated", "guardrail.disabled",
            "boundary.created",
        }
        assert TRUST_AUDIT_ACTIONS == expected

    def test_registry_is_frozen(self):
        from app.trustplane.services.audit import TRUST_AUDIT_ACTIONS
        with pytest.raises(AttributeError):
            TRUST_AUDIT_ACTIONS.add("bad.action")


class TestResponseSchemas:
    """Test response schema from_attributes works."""

    def test_system_response_from_attributes(self):
        from app.trustplane.schemas.inventory import SystemResponse
        # Verify model_config is set
        assert SystemResponse.model_config.get("from_attributes") is True

    def test_assessment_response_from_attributes(self):
        from app.trustplane.schemas.risk import AssessmentResponse
        assert AssessmentResponse.model_config.get("from_attributes") is True

    def test_policy_response_from_attributes(self):
        from app.trustplane.schemas.risk import PolicyResponse
        assert PolicyResponse.model_config.get("from_attributes") is True

    def test_audit_response_from_attributes(self):
        from app.trustplane.schemas.risk import TrustAuditEventResponse
        assert TrustAuditEventResponse.model_config.get("from_attributes") is True


class TestSlugGeneration:
    """Test slug generation utility."""

    def test_basic_slug(self):
        from app.trustplane.services.inventory import _slugify
        assert _slugify("My AI System") == "my-ai-system"

    def test_special_chars(self):
        from app.trustplane.services.inventory import _slugify
        assert _slugify("AI: Content Moderation (v2)") == "ai-content-moderation-v2"

    def test_truncation(self):
        from app.trustplane.services.inventory import _slugify
        result = _slugify("x" * 200)
        assert len(result) <= 100

    def test_strip_hyphens(self):
        from app.trustplane.services.inventory import _slugify
        assert _slugify("--test--") == "test"


class TestDefaultDimensions:
    """Validate the seeded default dimensions and thresholds."""

    def test_default_dimensions_count(self):
        from app.trustplane.models.risk import DEFAULT_DIMENSIONS
        assert len(DEFAULT_DIMENSIONS) == 8

    def test_default_dimensions_keys_unique(self):
        from app.trustplane.models.risk import DEFAULT_DIMENSIONS
        keys = [d["key"] for d in DEFAULT_DIMENSIONS]
        assert len(keys) == len(set(keys))

    def test_default_dimensions_have_required_fields(self):
        from app.trustplane.models.risk import DEFAULT_DIMENSIONS
        required = {"key", "label", "description", "weight", "scale_min", "scale_max", "guidance"}
        for dim in DEFAULT_DIMENSIONS:
            assert required.issubset(dim.keys()), f"Missing fields in {dim['key']}"

    def test_default_dimensions_weights_positive(self):
        from app.trustplane.models.risk import DEFAULT_DIMENSIONS
        for dim in DEFAULT_DIMENSIONS:
            assert dim["weight"] > 0, f"Non-positive weight for {dim['key']}"

    def test_default_thresholds_coverage(self):
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        assert set(DEFAULT_TIER_THRESHOLDS.keys()) == {"minimal", "low", "medium", "high", "critical"}

    def test_default_thresholds_monotonic(self):
        from app.trustplane.models.risk import DEFAULT_TIER_THRESHOLDS
        scores = [
            DEFAULT_TIER_THRESHOLDS["minimal"]["max_score"],
            DEFAULT_TIER_THRESHOLDS["low"]["max_score"],
            DEFAULT_TIER_THRESHOLDS["medium"]["max_score"],
            DEFAULT_TIER_THRESHOLDS["high"]["max_score"],
        ]
        assert scores == sorted(scores), "Thresholds must be monotonically increasing"


# ── Phase 2: Evidence & Review schema tests ──────────────────────────


class TestCaseSchemaValidation:

    def test_create_case_rejects_empty_title(self):
        from app.trustplane.schemas.evidence import CreateCaseRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateCaseRequest(system_id="x", title="  ", claim="test claim")

    def test_create_case_rejects_long_title(self):
        from app.trustplane.schemas.evidence import CreateCaseRequest
        with pytest.raises(ValueError, match="300 characters"):
            CreateCaseRequest(system_id="x", title="x" * 301, claim="test claim")

    def test_create_case_rejects_empty_claim(self):
        from app.trustplane.schemas.evidence import CreateCaseRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateCaseRequest(system_id="x", title="Test", claim="  ")

    def test_create_case_accepts_valid(self):
        from app.trustplane.schemas.evidence import CreateCaseRequest
        req = CreateCaseRequest(
            system_id="sys01", title="Safety Claim",
            claim="The system does not produce harmful outputs",
        )
        assert req.title == "Safety Claim"

    def test_change_status_rejects_invalid(self):
        from app.trustplane.schemas.evidence import ChangeCaseStatusRequest
        with pytest.raises(ValueError, match="status must be one of"):
            ChangeCaseStatusRequest(status="invalid")

    def test_change_status_accepts_valid(self):
        from app.trustplane.schemas.evidence import ChangeCaseStatusRequest
        for s in ("draft", "active", "challenged", "retired"):
            req = ChangeCaseStatusRequest(status=s)
            assert req.status == s


class TestEvidenceSchemaValidation:

    def test_create_evidence_rejects_invalid_type(self):
        from app.trustplane.schemas.evidence import CreateEvidenceRequest
        with pytest.raises(ValueError, match="evidence_type must be one of"):
            CreateEvidenceRequest(title="Test", evidence_type="invalid")

    def test_create_evidence_accepts_all_types(self):
        from app.trustplane.schemas.evidence import CreateEvidenceRequest, VALID_EVIDENCE_TYPES
        for t in VALID_EVIDENCE_TYPES:
            req = CreateEvidenceRequest(title="Test", evidence_type=t)
            assert req.evidence_type == t

    def test_create_evidence_rejects_ctrl_in_title(self):
        from app.trustplane.schemas.evidence import CreateEvidenceRequest
        with pytest.raises(ValueError, match="control characters"):
            CreateEvidenceRequest(title="test\x00", evidence_type="benchmark")

    def test_change_evidence_status_rejects_invalid(self):
        from app.trustplane.schemas.evidence import ChangeEvidenceStatusRequest
        with pytest.raises(ValueError, match="status must be one of"):
            ChangeEvidenceStatusRequest(status="invalid")


class TestLinkSchemaValidation:

    def test_link_rejects_invalid_relation(self):
        from app.trustplane.schemas.evidence import LinkEvidenceRequest
        with pytest.raises(ValueError, match="relation must be one of"):
            LinkEvidenceRequest(evidence_id="e01", relation="invalid")

    def test_link_accepts_valid_relations(self):
        from app.trustplane.schemas.evidence import LinkEvidenceRequest
        for r in ("supports", "weakens", "mitigates", "depends_on"):
            req = LinkEvidenceRequest(evidence_id="e01", relation=r)
            assert req.relation == r


class TestReviewSchemaValidation:

    def test_create_review_rejects_invalid_type(self):
        from app.trustplane.schemas.evidence import CreateReviewRequest
        with pytest.raises(ValueError, match="review_type must be one of"):
            CreateReviewRequest(
                review_type="invalid", title="Test",
                target_type="ai_system", target_id="s01",
            )

    def test_create_review_accepts_valid(self):
        from app.trustplane.schemas.evidence import CreateReviewRequest
        req = CreateReviewRequest(
            review_type="risk_assessment", title="Review risk",
            target_type="ai_system", target_id="s01",
        )
        assert req.review_type == "risk_assessment"

    def test_decide_rejects_invalid_decision(self):
        from app.trustplane.schemas.evidence import DecideReviewRequest
        with pytest.raises(ValueError, match="decision must be one of"):
            DecideReviewRequest(decision="invalid", rationale="reason")

    def test_decide_rejects_empty_rationale(self):
        from app.trustplane.schemas.evidence import DecideReviewRequest
        with pytest.raises(ValueError, match="must not be empty"):
            DecideReviewRequest(decision="approve", rationale="  ")

    def test_decide_accepts_valid(self):
        from app.trustplane.schemas.evidence import DecideReviewRequest
        for d in ("approve", "reject", "return", "escalate"):
            req = DecideReviewRequest(decision=d, rationale="Good reason")
            assert req.decision == d


class TestPhase2AuditRegistry:
    """Verify Phase 2 actions are in the canonical registry."""

    def test_evidence_actions_registered(self):
        from app.trustplane.services.audit import TRUST_AUDIT_ACTIONS
        phase2_actions = {
            "case.created", "case.updated", "case.status_changed",
            "evidence.created", "evidence.updated", "evidence.status_changed",
            "evidence.linked", "evidence.unlinked",
            "review.created", "review.assigned", "review.decided",
            "review.cancelled", "review.expired",
        }
        assert phase2_actions.issubset(TRUST_AUDIT_ACTIONS)


class TestPhase2ResponseSchemas:

    def test_case_response_from_attributes(self):
        from app.trustplane.schemas.evidence import CaseResponse
        assert CaseResponse.model_config.get("from_attributes") is True

    def test_evidence_response_from_attributes(self):
        from app.trustplane.schemas.evidence import EvidenceResponse
        assert EvidenceResponse.model_config.get("from_attributes") is True

    def test_review_response_from_attributes(self):
        from app.trustplane.schemas.evidence import ReviewResponse
        assert ReviewResponse.model_config.get("from_attributes") is True

    def test_decision_response_from_attributes(self):
        from app.trustplane.schemas.evidence import DecisionResponse
        assert DecisionResponse.model_config.get("from_attributes") is True


# ── Phase 3-4: Gates & Guardrails schema tests ──────────────────────


class TestProfileSchemaValidation:

    def test_create_profile_rejects_invalid_trigger(self):
        from app.trustplane.schemas.gates import CreateProfileRequest
        with pytest.raises(ValueError, match="trigger must be one of"):
            CreateProfileRequest(name="Test", trigger="invalid")

    def test_create_profile_accepts_valid(self):
        from app.trustplane.schemas.gates import CreateProfileRequest, VALID_GATE_TRIGGERS
        for t in VALID_GATE_TRIGGERS:
            req = CreateProfileRequest(name="Test", trigger=t)
            assert req.trigger == t

    def test_create_profile_rejects_empty_name(self):
        from app.trustplane.schemas.gates import CreateProfileRequest
        with pytest.raises(ValueError, match="must not be empty"):
            CreateProfileRequest(name="  ", trigger="publish_pack")


class TestCheckSchemaValidation:

    def test_add_check_rejects_invalid_type(self):
        from app.trustplane.schemas.gates import AddCheckRequest
        with pytest.raises(ValueError, match="check_type must be one of"):
            AddCheckRequest(name="Test", check_type="invalid")

    def test_add_check_accepts_valid(self):
        from app.trustplane.schemas.gates import AddCheckRequest, VALID_CHECK_TYPES
        for t in VALID_CHECK_TYPES:
            req = AddCheckRequest(name="Test", check_type=t)
            assert req.check_type == t


class TestGateResultSchemaValidation:

    def test_evaluate_gate_rejects_bad_outcome(self):
        from app.trustplane.schemas.gates import EvaluateGateRequest
        with pytest.raises(ValueError, match="outcome must be"):
            EvaluateGateRequest(
                profile_id="p01", target_type="pack", target_id="t01",
                check_results=[{"check_id": "c01", "outcome": "bad"}],
            )

    def test_evaluate_gate_rejects_missing_fields(self):
        from app.trustplane.schemas.gates import EvaluateGateRequest
        with pytest.raises(ValueError, match="must have check_id"):
            EvaluateGateRequest(
                profile_id="p01", target_type="pack", target_id="t01",
                check_results=[{"outcome": "passed"}],
            )

    def test_override_gate_rejects_empty_justification(self):
        from app.trustplane.schemas.gates import OverrideGateRequest
        with pytest.raises(ValueError, match="must not be empty"):
            OverrideGateRequest(justification="  ")


class TestGuardrailSchemaValidation:

    def test_create_guardrail_rejects_invalid_type(self):
        from app.trustplane.schemas.gates import CreateGuardrailRequest
        with pytest.raises(ValueError, match="guardrail_type must be one of"):
            CreateGuardrailRequest(name="Test", guardrail_type="invalid", config={})

    def test_create_guardrail_accepts_valid(self):
        from app.trustplane.schemas.gates import CreateGuardrailRequest, VALID_GUARDRAIL_TYPES
        for t in VALID_GUARDRAIL_TYPES:
            req = CreateGuardrailRequest(name="Test", guardrail_type=t, config={"rule": True})
            assert req.guardrail_type == t


class TestBoundarySchemaValidation:

    def test_create_boundary_rejects_invalid_type(self):
        from app.trustplane.schemas.gates import CreateBoundaryRequest
        with pytest.raises(ValueError, match="boundary_type must be one of"):
            CreateBoundaryRequest(name="Test", boundary_type="invalid", limit_value=100)

    def test_create_boundary_rejects_zero_limit(self):
        from app.trustplane.schemas.gates import CreateBoundaryRequest
        with pytest.raises(ValueError, match="must be positive"):
            CreateBoundaryRequest(name="Test", boundary_type="spend_ceiling", limit_value=0)

    def test_create_boundary_rejects_invalid_period(self):
        from app.trustplane.schemas.gates import CreateBoundaryRequest
        with pytest.raises(ValueError, match="must be hour, day"):
            CreateBoundaryRequest(
                name="Test", boundary_type="rate_limit",
                limit_value=100, limit_period="minute",
            )

    def test_create_boundary_accepts_valid(self):
        from app.trustplane.schemas.gates import CreateBoundaryRequest
        req = CreateBoundaryRequest(
            name="API calls", boundary_type="rate_limit",
            limit_value=1000, limit_period="hour",
        )
        assert req.limit_value == 1000
        assert req.limit_period == "hour"


class TestPhase34AuditRegistry:

    def test_gate_actions_registered(self):
        from app.trustplane.services.audit import TRUST_AUDIT_ACTIONS
        phase34_actions = {
            "profile.created", "profile.activated",
            "gate.evaluated", "gate.overridden",
            "guardrail.created", "guardrail.activated", "guardrail.disabled",
            "boundary.created",
        }
        assert phase34_actions.issubset(TRUST_AUDIT_ACTIONS)


class TestPhase34ResponseSchemas:

    def test_profile_response(self):
        from app.trustplane.schemas.gates import ProfileResponse
        assert ProfileResponse.model_config.get("from_attributes") is True

    def test_check_response(self):
        from app.trustplane.schemas.gates import CheckResponse
        assert CheckResponse.model_config.get("from_attributes") is True

    def test_gate_result_response(self):
        from app.trustplane.schemas.gates import GateResultResponse
        assert GateResultResponse.model_config.get("from_attributes") is True

    def test_guardrail_response(self):
        from app.trustplane.schemas.gates import GuardrailResponse
        assert GuardrailResponse.model_config.get("from_attributes") is True

    def test_boundary_response(self):
        from app.trustplane.schemas.gates import BoundaryResponse
        assert BoundaryResponse.model_config.get("from_attributes") is True
