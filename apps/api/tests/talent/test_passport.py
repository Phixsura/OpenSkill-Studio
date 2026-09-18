"""Skill Passport tests — privacy defaults, schema validation."""

import pytest

from app.talent.models.passport import PASSPORT_SHAREABLE_FIELDS


class TestPassportConstants:
    def test_shareable_fields_complete(self):
        assert "capabilities" in PASSPORT_SHAREABLE_FIELDS
        assert "credentials" in PASSPORT_SHAREABLE_FIELDS
        assert "portfolio" in PASSPORT_SHAREABLE_FIELDS
        assert "availability" in PASSPORT_SHAREABLE_FIELDS
        assert len(PASSPORT_SHAREABLE_FIELDS) == 9


# ---- API tests ----


@pytest.mark.asyncio
async def test_get_passport_requires_auth(client):
    response = await client.get("/api/v1/talent/passport")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_passport_requires_auth(client):
    response = await client.patch("/api/v1/talent/passport", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_snapshot_requires_auth(client):
    response = await client.post("/api/v1/talent/passport/snapshots", json={})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_snapshots_requires_auth(client):
    response = await client.get("/api/v1/talent/passport/snapshots")
    assert response.status_code == 401


def test_verify_snapshot_not_401():
    """Public verification endpoint does NOT require auth.

    Verify the route definition — the actual HTTP call hangs in
    noop-lifespan (no DB pool), so we check the function signature
    to confirm it doesn't require authentication.
    """
    import inspect

    from app.talent.api.passport import verify_passport

    sig = inspect.signature(verify_passport)
    param_names = list(sig.parameters.keys())
    # Should NOT have 'user' parameter (no auth dependency)
    assert "user" not in param_names, "verify_passport should be public (no auth)"
    assert "share_token" in param_names
