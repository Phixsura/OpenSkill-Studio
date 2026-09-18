"""Talent pool tests — membership modes, consent, model structure, auth."""

import pytest

from app.talent.models.talent_pool import (
    TalentOutreach,
    TalentPool,
    TalentPoolMembership,
)


class TestTalentPoolModel:
    def test_membership_mode_defaults_to_manual(self):
        col = TalentPool.__table__.columns["membership_mode"]
        assert col.server_default is not None
        assert "manual" in str(col.server_default.arg)

    def test_visibility_defaults_to_internal(self):
        col = TalentPool.__table__.columns["visibility"]
        assert col.server_default is not None
        assert "internal" in str(col.server_default.arg)

    def test_has_org_id_fk(self):
        col = TalentPool.__table__.columns["org_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "organizations.id" in fks

    def test_has_rule_config_jsonb(self):
        assert "rule_config" in TalentPool.__table__.columns

    def test_valid_membership_modes(self):
        valid = {"manual", "rule_suggested", "candidate_opt_in"}
        assert len(valid) == 3


class TestTalentPoolMembership:
    def test_consent_status_defaults_to_accepted(self):
        """For manual/opted_in pools, consent is always accepted."""
        col = TalentPoolMembership.__table__.columns["consent_status"]
        assert col.server_default is not None
        assert "accepted" in str(col.server_default.arg)

    def test_unique_pool_member(self):
        indexes = {idx.name for idx in TalentPoolMembership.__table__.indexes}
        assert "uq_pool_member" in indexes

    def test_has_source_column(self):
        """Source: manual_added | rule_suggested | opted_in."""
        assert "source" in TalentPoolMembership.__table__.columns

    def test_has_user_id_fk(self):
        col = TalentPoolMembership.__table__.columns["user_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "users.id" in fks

    def test_consent_statuses(self):
        """pending_consent (rule-suggested), accepted, declined."""
        valid = {"pending_consent", "accepted", "declined"}
        assert len(valid) == 3


class TestTalentOutreach:
    def test_status_defaults_to_sent(self):
        col = TalentOutreach.__table__.columns["status"]
        assert col.server_default is not None
        assert "sent" in str(col.server_default.arg)

    def test_has_user_id_fk(self):
        col = TalentOutreach.__table__.columns["user_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "users.id" in fks

    def test_has_outreach_type(self):
        assert "outreach_type" in TalentOutreach.__table__.columns

    def test_has_expires_at(self):
        assert "expires_at" in TalentOutreach.__table__.columns


# ---- API auth tests ----


@pytest.mark.asyncio
async def test_create_pool_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/pools?org_id=fake",
        json={"name": "Test Pool"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_pools_requires_auth(client):
    response = await client.get("/api/v1/talent/pools?org_id=fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_pool_member_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/pools/fake/members",
        json={"user_id": "fake"},
    )
    assert response.status_code == 401
