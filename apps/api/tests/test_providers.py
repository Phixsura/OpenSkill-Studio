"""Tests for capability taxonomy + provider four-entity model (Issue #21, ADR-011)."""

import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def c():
    from app.core.database import engine
    from app.main import app

    orig = app.router.lifespan_context

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


def _email():
    return f"prov-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Prov"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"P-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


async def _mock_adapter_id(c, h):
    r = await c.get("/api/v1/providers/adapters", headers=h)
    assert r.status_code == 200
    adapters = r.json()["data"]
    mock = next(a for a in adapters if a["key"] == "mock")
    return mock["id"]


async def _anthropic_adapter_id(c, h):
    r = await c.get("/api/v1/providers/adapters", headers=h)
    adapters = r.json()["data"]
    return next(a for a in adapters if a["key"] == "anthropic")["id"]


# ── Catalogs ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_capabilities_seeded(c):
    h, _ = await _auth(c)
    r = await c.get("/api/v1/capabilities", headers=h)
    assert r.status_code == 200
    keys = {cap["key"] for cap in r.json()["data"]}
    assert {"image_generation", "image_to_video", "multimodal_review"} <= keys
    # io_signature is machine-readable
    img_gen = next(cap for cap in r.json()["data"] if cap["key"] == "image_generation")
    assert img_gen["io_signature"]["outputs"] == ["image"]


@pytest.mark.asyncio
async def test_list_adapters_seeded(c):
    h, _ = await _auth(c)
    r = await c.get("/api/v1/providers/adapters", headers=h)
    assert r.status_code == 200
    keys = {a["key"] for a in r.json()["data"]}
    assert {"mock", "anthropic"} <= keys
    # Anthropic declares credential FIELD NAMES only
    anth = next(a for a in r.json()["data"] if a["key"] == "anthropic")
    assert anth["credential_fields"] == ["api_key"]


@pytest.mark.asyncio
async def test_catalogs_require_auth(c):
    r = await c.get("/api/v1/capabilities")
    assert r.status_code == 401
    r2 = await c.get("/api/v1/providers/adapters")
    assert r2.status_code == 401


# ── Connections ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_connection_no_credentials(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "Mock Conn"},
        headers=h,
    )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["name"] == "Mock Conn"
    assert data["credential_id"] is None
    assert data["status"] == "active"
    # No credential material anywhere in response
    assert "credentials" not in data
    assert "encrypted_data" not in data


@pytest.mark.asyncio
async def test_create_connection_with_credentials_write_only(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _anthropic_adapter_id(c, h)
    secret = f"sk-test-{uuid.uuid4().hex}"
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "Claude", "credentials": {"api_key": secret}},
        headers=h,
    )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["credential_id"] is not None
    # The secret NEVER appears in any response
    assert secret not in r.text

    # GET must not leak it either
    r2 = await c.get(f"/api/v1/orgs/{oid}/provider-connections/{data['id']}", headers=h)
    assert r2.status_code == 200
    assert secret not in r2.text

    # List must not leak it
    r3 = await c.get(f"/api/v1/orgs/{oid}/provider-connections", headers=h)
    assert secret not in r3.text


@pytest.mark.asyncio
async def test_credential_encryption_roundtrip():
    from app.core.crypto import decrypt_credentials, encrypt_credentials

    data = {"api_key": "sk-secret-123", "region": "us"}
    token = encrypt_credentials(data)
    assert "sk-secret-123" not in token
    assert decrypt_credentials(token) == data


@pytest.mark.asyncio
async def test_credential_in_config_rejected(c):
    """Credential field names must not be smuggled into non-sensitive config."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _anthropic_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "Bad", "config": {"api_key": "sk-leaked"}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "CREDENTIAL_IN_CONFIG"


@pytest.mark.asyncio
async def test_unknown_credential_field_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _anthropic_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "Bad", "credentials": {"password": "x"}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "UNKNOWN_CREDENTIAL_FIELD"


@pytest.mark.asyncio
async def test_connection_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    aid = await _mock_adapter_id(c, h1)
    r = await c.post(
        f"/api/v1/orgs/{o1}/provider-connections",
        json={"adapter_id": aid, "name": "Org1 Conn"},
        headers=h1,
    )
    conn_id = r.json()["data"]["id"]

    # Org 2 user cannot see or touch org 1's connection
    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.get(f"/api/v1/orgs/{o2}/provider-connections/{conn_id}", headers=h2)
    assert r2.status_code == 404
    # Nor through org1's path (not a member)
    r3 = await c.get(f"/api/v1/orgs/{o1}/provider-connections/{conn_id}", headers=h2)
    assert r3.status_code in (403, 404)


@pytest.mark.asyncio
async def test_student_cannot_create_connection(c):
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    aid = await _mock_adapter_id(c, h_owner)

    h_student, u_student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": u_student["id"], "role": "student"},
        headers=h_owner,
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "Nope"},
        headers=h_student,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_update_and_delete_connection(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "ToUpdate"},
        headers=h,
    )
    conn_id = r.json()["data"]["id"]

    r2 = await c.put(
        f"/api/v1/orgs/{oid}/provider-connections/{conn_id}",
        json={"name": "Updated", "status": "disabled"},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["name"] == "Updated"
    assert r2.json()["data"]["status"] == "disabled"

    r3 = await c.delete(f"/api/v1/orgs/{oid}/provider-connections/{conn_id}", headers=h)
    assert r3.status_code == 204
    r4 = await c.get(f"/api/v1/orgs/{oid}/provider-connections/{conn_id}", headers=h)
    assert r4.status_code == 404


# ── Offerings ─────────────────────────────────────────────


async def _connection(c, h, oid):
    aid = await _mock_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": f"Conn-{uuid.uuid4().hex[:4]}"},
        headers=h,
    )
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_create_offering(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "mock-image-v1",
            "features": ["style_reference"],
            "quality_tier": "standard",
        },
        headers=h,
    )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["capability_key"] == "image_generation"
    assert data["features"] == ["style_reference"]


@pytest.mark.asyncio
async def test_offering_unknown_capability_rejected(c):
    """Closed vocabulary: unknown capability keys are rejected at creation."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "teleportation",
            "model_name": "nope",
        },
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "UNKNOWN_CAPABILITY"


@pytest.mark.asyncio
async def test_list_offerings_filter_by_capability(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    for cap, model in [("image_generation", "m1"), ("image_to_video", "m2")]:
        await c.post(
            f"/api/v1/orgs/{oid}/provider-offerings",
            json={"connection_id": conn_id, "capability_key": cap, "model_name": model},
            headers=h,
        )
    r = await c.get(
        f"/api/v1/orgs/{oid}/provider-offerings?capability=image_to_video", headers=h
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 1
    assert data[0]["model_name"] == "m2"


@pytest.mark.asyncio
async def test_offering_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    conn_id = await _connection(c, h1, o1)
    r = await c.post(
        f"/api/v1/orgs/{o1}/provider-offerings",
        json={"connection_id": conn_id, "capability_key": "upscale", "model_name": "up1"},
        headers=h1,
    )
    off_id = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.put(
        f"/api/v1/orgs/{o2}/provider-offerings/{off_id}",
        json={"model_name": "hijacked"},
        headers=h2,
    )
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_capability_check_service():
    """check_capabilities returns gaps for unsatisfied requirements."""
    from unittest.mock import AsyncMock

    from app.services.provider import ProviderService

    svc = ProviderService(AsyncMock())
    svc.list_offerings = AsyncMock(return_value=[])
    gaps = await svc.check_capabilities("org1", [{"capability": "image_generation", "features": []}])
    assert len(gaps) == 1
    assert gaps[0]["code"] == "CAPABILITY_UNSATISFIED"
    assert gaps[0]["capability"] == "image_generation"
