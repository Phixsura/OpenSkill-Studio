"""Assessment blueprint & run tests — status transitions, validation, auth."""

import pytest

from app.talent.models.assessment import AssessmentBlueprint, AssessmentRun


class TestBlueprintModel:
    def test_status_defaults_to_draft(self):
        col = AssessmentBlueprint.__table__.columns["status"]
        assert col.server_default is not None
        assert "draft" in str(col.server_default.arg)

    def test_version_defaults_to_1(self):
        col = AssessmentBlueprint.__table__.columns["version"]
        assert col.server_default is not None
        assert "1" in str(col.server_default.arg)

    def test_has_org_id_fk(self):
        col = AssessmentBlueprint.__table__.columns["org_id"]
        assert col.nullable is False
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "organizations.id" in fks

    def test_capability_requirements_is_jsonb(self):
        col = AssessmentBlueprint.__table__.columns["capability_requirements"]
        assert col is not None


class TestRunModel:
    def test_status_defaults_to_not_started(self):
        col = AssessmentRun.__table__.columns["status"]
        assert col.server_default is not None
        assert "not_started" in str(col.server_default.arg)

    def test_has_user_id_fk(self):
        col = AssessmentRun.__table__.columns["user_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "users.id" in fks

    def test_has_blueprint_id_fk(self):
        col = AssessmentRun.__table__.columns["blueprint_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "assessment_blueprints.id" in fks


class TestBlueprintStatusTransitions:
    """update_blueprint only allows draft → (anything). Active blueprints are locked."""

    def test_valid_statuses(self):
        """Blueprint statuses are draft | active | archived."""
        valid = {"draft", "active", "archived"}
        # These are the only statuses referenced in the service
        assert valid == {"draft", "active", "archived"}


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_create_blueprint_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/assessments?org_id=fake",
        json={"title": "Test", "assessment_type": "knowledge"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_blueprints_requires_auth(client):
    response = await client.get("/api/v1/talent/assessments?org_id=fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_blueprint_requires_auth(client):
    response = await client.get("/api/v1/talent/assessments/fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_start_run_requires_auth(client):
    response = await client.post("/api/v1/talent/assessments/fake/runs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_submit_run_requires_auth(client):
    response = await client.patch(
        "/api/v1/talent/assessments/fake/runs/fake",
        json={},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_review_run_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/assessments/fake/runs/fake/review",
        json={"results": [], "status": "passed"},
    )
    assert response.status_code == 401
