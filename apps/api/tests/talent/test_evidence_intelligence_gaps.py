"""Tests for gaps #21-35: Evidence & Scoring Intelligence."""

from datetime import UTC, datetime, timedelta

from app.talent.services.evidence_intelligence import (
    DEFAULT_CALIBRATION,
    DISPUTE_REASONS,
    DISPUTE_STATUSES,
    EVIDENCE_GENERATION_HOOKS,
    QUALITY_FACTORS,
    build_auto_evidence,
    compute_evidence_quality,
    get_hook_config,
    simulate_score_change,
    validate_calibration,
    validate_dispute,
)


# Gap #21: Evidence quality scoring
class TestEvidenceQuality:
    def test_high_quality(self):
        ev = {
            "source_id": "src1",
            "score_normalized": 0.9,
            "verification_level": "employer_verified",
            "occurred_at": datetime.now(UTC),
            "org_id": "org1",
            "confidence": 0.95,
        }
        result = compute_evidence_quality(ev)
        assert result["quality_score"] > 0.7
        assert "factors" in result

    def test_low_quality(self):
        ev = {
            "source_id": None,
            "score_normalized": None,
            "verification_level": "self_reported",
            "occurred_at": datetime.now(UTC) - timedelta(days=800),
            "org_id": None,
            "confidence": 0.3,
        }
        result = compute_evidence_quality(ev)
        assert result["quality_score"] < 0.4

    def test_all_factors_present(self):
        ev = {"verification_level": "peer_verified", "occurred_at": datetime.now(UTC)}
        result = compute_evidence_quality(ev)
        assert set(result["factors"].keys()) == set(QUALITY_FACTORS.keys())


# Gap #24: Dispute validation
class TestDisputeValidation:
    def test_valid_dispute(self):
        errors = validate_dispute(
            reason="inaccurate_score",
            details="The score does not reflect my actual work on this project",
        )
        assert len(errors) == 0

    def test_invalid_reason(self):
        errors = validate_dispute(reason="invalid", details="Some valid details here")
        assert any("reason" in e.lower() for e in errors)

    def test_short_details(self):
        errors = validate_dispute(reason="inaccurate_score", details="short")
        assert any("details" in e.lower() for e in errors)

    def test_dispute_constants(self):
        assert "open" in DISPUTE_STATUSES
        assert "resolved_upheld" in DISPUTE_STATUSES
        assert "inaccurate_score" in DISPUTE_REASONS
        assert "not_my_work" in DISPUTE_REASONS


# Gap #26: Scoring simulation
class TestScoringSimulation:
    def test_simulation_improves_score(self):
        current = [
            {
                "score_normalized": 0.5,
                "verification_level": "self_reported",
                "confidence": 0.8,
                "occurred_at": datetime.now(UTC),
                "status": "active",
                "expires_at": None,
            },
        ]
        new = {
            "score_normalized": 0.9,
            "verification_level": "employer_verified",
            "confidence": 1.0,
            "occurred_at": datetime.now(UTC),
            "status": "active",
            "expires_at": None,
        }
        result = simulate_score_change(current, new)
        assert result["score_delta"] > 0
        assert result["projected_score"] > result["current_score"]

    def test_simulation_with_empty_current(self):
        result = simulate_score_change(
            [],
            {
                "score_normalized": 0.8,
                "verification_level": "instructor_verified",
                "confidence": 1.0,
                "occurred_at": datetime.now(UTC),
                "status": "active",
                "expires_at": None,
            },
        )
        assert result["current_score"] == 0.0
        assert result["projected_score"] > 0


# Gap #28: Calibration
class TestCalibration:
    def test_default_calibration_valid(self):
        errors = validate_calibration(DEFAULT_CALIBRATION)
        assert len(errors) == 0

    def test_invalid_weights(self):
        config = {"dimension_weights": {"depth": 0.5, "breadth": 0.5, "recency": 0.5}}
        errors = validate_calibration(config)
        assert any("sum" in e.lower() for e in errors)

    def test_invalid_k(self):
        errors = validate_calibration({"shrinkage_k": -1})
        assert len(errors) > 0

    def test_default_structure(self):
        assert "shrinkage_k" in DEFAULT_CALIBRATION
        assert "dimension_weights" in DEFAULT_CALIBRATION
        assert "verification_weights" in DEFAULT_CALIBRATION


# Gap #35: Automated evidence hooks
class TestAutoEvidence:
    def test_known_hook(self):
        hook = get_hook_config("project_approval")
        assert hook is not None
        assert hook["verification_level"] == "instructor_verified"

    def test_unknown_hook(self):
        assert get_hook_config("nonexistent") is None

    def test_build_auto_evidence(self):
        ev = build_auto_evidence(
            user_id="u1",
            capability_id="c1",
            trigger_type="assessment_pass",
            source_type="assessment_result",
            source_id="a1",
        )
        assert ev is not None
        assert ev["verification_level"] == "assessment_verified"
        assert ev["confidence"] == 0.95

    def test_build_unknown_trigger(self):
        ev = build_auto_evidence(
            user_id="u1",
            capability_id="c1",
            trigger_type="nonexistent",
            source_type="unknown",
            source_id="x",
        )
        assert ev is None

    def test_all_hooks_defined(self):
        assert len(EVIDENCE_GENERATION_HOOKS) >= 6
        for hook in EVIDENCE_GENERATION_HOOKS.values():
            assert "verification_level" in hook
            assert "confidence" in hook
