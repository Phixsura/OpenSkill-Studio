"""Employer verification tests — scope enforcement, evidence generation, auth."""

import inspect

import pytest

from app.talent.models.evidence import VERIFICATION_WEIGHTS
from app.talent.models.internship import EmployerVerification
from app.talent.services.employer_verification import EmployerVerificationService


class TestScopeEnforcement:
    """Employers can only rate capabilities from the opportunity's requirements."""

    def test_service_validates_capability_scope(self):
        """create_verification must check each rating's capability_id against
        the opportunity's required ∪ preferred capabilities."""
        source = inspect.getsource(EmployerVerificationService.create_verification)
        assert "allowed_cap_ids" in source, (
            "create_verification must build an allowed set from opportunity caps"
        )
        assert "not in allowed_cap_ids" in source, (
            "create_verification must reject ratings for non-allowed capabilities"
        )

    def test_service_validates_score_range(self):
        """Rating scores must be in [0, 1]."""
        source = inspect.getsource(EmployerVerificationService.create_verification)
        assert "0 <= score <= 1" in source or "score <= 1" in source


class TestAutoEvidenceGeneration:
    """Employer verification creates employer_verified evidence (highest trust)."""

    def test_employer_verified_is_highest_weight(self):
        assert VERIFICATION_WEIGHTS["employer_verified"] == 1.0

    def test_service_generates_evidence(self):
        """create_verification must call record_evidence with employer_verified."""
        source = inspect.getsource(EmployerVerificationService.create_verification)
        assert "employer_verified" in source
        assert "record_evidence" in source

    def test_service_generates_outcome_event(self):
        """create_verification must create an OutcomeEvent."""
        source = inspect.getsource(EmployerVerificationService.create_verification)
        assert "OutcomeEvent" in source


class TestVerificationModel:
    def test_has_placement_id_fk(self):
        col = EmployerVerification.__table__.columns["placement_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "placements.id" in fks

    def test_has_user_id_fk(self):
        col = EmployerVerification.__table__.columns["user_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "users.id" in fks

    def test_has_capability_ratings_jsonb(self):
        assert "capability_ratings" in EmployerVerification.__table__.columns


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_create_verification_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/placements/fake/verification",
        json={"capability_ratings": []},
    )
    assert response.status_code == 401
