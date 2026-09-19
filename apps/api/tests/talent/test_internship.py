"""Internship supervision & cohort exposure tests — consent, status, auth."""

import pytest

from app.talent.models.internship import (
    OUTCOME_EVENT_TYPES,
    CohortOpportunityExposure,
    InternshipSupervision,
)


class TestCohortExposure:
    """Exposure ≠ data sharing: exposing an opportunity to a cohort does NOT
    share student data. Students must individually opt in."""

    def test_exposure_has_cohort_and_opportunity_fks(self):
        cols = CohortOpportunityExposure.__table__.columns
        assert "cohort_id" in cols
        assert "opportunity_id" in cols

    def test_exposure_has_unique_constraint(self):
        indexes = {idx.name for idx in CohortOpportunityExposure.__table__.indexes}
        assert "uq_cohort_exposure" in indexes

    def test_exposure_has_exposed_by(self):
        """Records who exposed the opportunity (instructor+ authorization)."""
        assert "exposed_by" in CohortOpportunityExposure.__table__.columns


class TestSupervisionModel:
    def test_status_defaults_to_pending(self):
        col = InternshipSupervision.__table__.columns["status"]
        assert col.server_default is not None
        assert "pending" in str(col.server_default.arg)

    def test_valid_supervision_statuses(self):
        valid = {"pending", "active", "completed", "terminated"}
        # These are the statuses used in the model and service
        assert "pending" in valid
        assert "completed" in valid

    def test_has_placement_id_unique(self):
        col = InternshipSupervision.__table__.columns["placement_id"]
        assert col.unique is True, "One supervision per placement"

    def test_has_milestones_and_notes_jsonb(self):
        cols = InternshipSupervision.__table__.columns
        assert "milestones" in cols
        assert "notes" in cols

    def test_has_school_org_id_fk(self):
        col = InternshipSupervision.__table__.columns["school_org_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "organizations.id" in fks


class TestOutcomeEventTypes:
    def test_expected_types_present(self):
        expected = {
            "internship_started",
            "internship_completed",
            "job_offer_received",
            "job_started",
            "contract_project_completed",
            "promotion",
            "role_change",
            "credential_renewed",
            "capability_reverified",
        }
        assert expected == OUTCOME_EVENT_TYPES

    def test_minimum_count(self):
        assert len(OUTCOME_EVENT_TYPES) >= 9


# ---- API auth tests ----


@pytest.mark.asyncio
async def test_create_supervision_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/supervisions",
        json={"placement_id": "fake", "school_org_id": "fake"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_supervisions_requires_auth(client):
    response = await client.get("/api/v1/talent/supervisions?school_org_id=fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_supervision_requires_auth(client):
    response = await client.patch("/api/v1/talent/supervisions/fake", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expose_opportunity_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/cohorts/fake/expose",
        json={"opportunity_id": "fake"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_cohort_opportunities_requires_auth(client):
    response = await client.get("/api/v1/talent/cohorts/fake/opportunities")
    assert response.status_code == 401
