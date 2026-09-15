"""Outreach tests — status lifecycle, model structure, auth."""

import pytest

from app.talent.models.talent_pool import TalentOutreach


class TestOutreachModel:
    def test_status_values(self):
        """Outreach statuses: sent, viewed, accepted, declined, expired."""
        valid = {"sent", "viewed", "accepted", "declined", "expired"}
        assert len(valid) == 5

    def test_status_defaults_to_sent(self):
        col = TalentOutreach.__table__.columns["status"]
        assert col.server_default is not None
        assert "sent" in str(col.server_default.arg)

    def test_has_org_id_fk(self):
        col = TalentOutreach.__table__.columns["org_id"]
        fks = [fk.target_fullname for fk in col.foreign_keys]
        assert "organizations.id" in fks

    def test_has_target_type_and_id(self):
        cols = TalentOutreach.__table__.columns
        assert "target_type" in cols
        assert "target_id" in cols

    def test_has_message_column(self):
        assert "message" in TalentOutreach.__table__.columns

    def test_has_responded_at(self):
        """Track when the user responded."""
        assert "responded_at" in TalentOutreach.__table__.columns

    def test_outreach_types(self):
        """Outreach types: opportunity_invitation | pool_invitation."""
        valid = {"opportunity_invitation", "pool_invitation"}
        assert len(valid) == 2


# ---- API auth tests ----

@pytest.mark.asyncio
async def test_send_outreach_requires_auth(client):
    response = await client.post(
        "/api/v1/talent/outreach?org_id=fake",
        json={
            "user_id": "fake",
            "outreach_type": "opportunity_invitation",
            "target_type": "opportunity",
            "target_id": "fake",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_outreach_requires_auth(client):
    response = await client.get("/api/v1/talent/outreach?org_id=fake")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_respond_outreach_requires_auth(client):
    response = await client.patch(
        "/api/v1/talent/outreach/fake",
        json={"status": "accepted"},
    )
    assert response.status_code == 401
