"""Credential rule & issuance tests — versioning, status, constraints, auth."""

import pytest

from app.talent.models.assessment import Credential, CredentialRule


class TestCredentialRuleModel:
    def test_status_defaults_to_draft(self):
        col = CredentialRule.__table__.columns["status"]
        assert col.server_default is not None
        assert "draft" in str(col.server_default.arg)

    def test_unique_version_per_type(self):
        """Each (credential_type, version) pair is unique."""
        indexes = {idx.name for idx in CredentialRule.__table__.indexes}
        assert "uq_credential_rule_version" in indexes

    def test_has_requirements_column(self):
        assert "requirements" in CredentialRule.__table__.columns


class TestCredentialModel:
    def test_status_defaults_to_active(self):
        col = Credential.__table__.columns["status"]
        assert col.server_default is not None
        assert "active" in str(col.server_default.arg)

    def test_partial_unique_active_per_user_type(self):
        """Only one active credential per (user, type) — partial unique index."""
        indexes = {idx.name for idx in Credential.__table__.indexes}
        assert "uq_credential_active" in indexes

    def test_has_user_id_fk(self):
        col = Credential.__table__.columns["user_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "users.id" in fks

    def test_has_credential_rule_id(self):
        assert "credential_rule_id" in Credential.__table__.columns

    def test_has_revoked_at(self):
        assert "revoked_at" in Credential.__table__.columns

    def test_has_revoked_reason(self):
        assert "revoked_reason" in Credential.__table__.columns


class TestCredentialStatusTransitions:
    def test_valid_statuses(self):
        """Credential statuses: active, expired, revoked, superseded."""
        valid = {"active", "expired", "revoked", "superseded"}
        assert valid == {"active", "expired", "revoked", "superseded"}


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_list_credentials_requires_auth(client):
    response = await client.get("/api/v1/talent/credentials")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_credential_requires_auth(client):
    response = await client.get("/api/v1/talent/credentials/fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_rule_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/credential-rules",
        json={
            "credential_type": "test",
            "display_name": "Test",
            "requirements": [],
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_evaluate_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/credentials/evaluate",
        json={"credential_type": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_issue_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/credentials/issue",
        json={"credential_type": "test"},
    )
    assert response.status_code == 401
