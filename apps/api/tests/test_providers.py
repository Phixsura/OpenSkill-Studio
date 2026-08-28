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
    from unittest.mock import AsyncMock, MagicMock

    from app.services.provider import ProviderService

    db = AsyncMock()
    # Single batched query returns no offerings (N+1 fix: one execute call)
    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=empty_result)
    svc = ProviderService(db)
    # THREE distinct capabilities: the pre-fix per-capability implementation
    # would issue 3 execute calls, so await_count == 1 actually pins the
    # batched single-query property (1 requirement couldn't distinguish them)
    gaps = await svc.check_capabilities(
        "org1",
        [
            {"capability": "image_generation", "features": []},
            {"capability": "image_to_video", "features": ["motion"]},
            {"capability": "upscale", "features": []},
        ],
    )
    assert len(gaps) == 3
    assert all(g["code"] == "CAPABILITY_UNSATISFIED" for g in gaps)
    assert {g["capability"] for g in gaps} == {
        "image_generation",
        "image_to_video",
        "upscale",
    }
    video_gap = next(g for g in gaps if g["capability"] == "image_to_video")
    assert video_gap["missing_features"] == ["motion"]
    # One query total regardless of requirement count (was one per capability)
    assert db.execute.await_count == 1


@pytest.mark.asyncio
async def test_capability_check_malformed_manifest_never_raises():
    """Manifest-controlled garbage (non-dict entries, non-string capability,
    non-list features) must yield MALFORMED_REQUIREMENT gaps — never a
    TypeError/500. A string features value must NOT degrade to per-character
    subset matching (set('highres') == {'h','i','g',...})."""
    from unittest.mock import AsyncMock, MagicMock

    from app.services.provider import ProviderService

    db = AsyncMock()
    # One offering satisfies 'image_generation' with no features
    offering = MagicMock()
    offering.capability_key = "image_generation"
    offering.features = []
    result = MagicMock()
    result.scalars.return_value.all.return_value = [offering]
    db.execute = AsyncMock(return_value=result)
    svc = ProviderService(db)

    gaps = await svc.check_capabilities(
        "org1",
        [
            "not-a-dict",
            {"capability": {"k": "v"}, "features": []},
            {"capability": "image_generation", "features": 5},
            {"capability": "image_generation", "features": "highres"},
        ],
    )
    malformed = [g for g in gaps if g["code"] == "MALFORMED_REQUIREMENT"]
    # non-dict entry + dict capability + int features + str features
    assert len(malformed) == 4
    # No gap ever reports per-character missing_features from 'highres'
    assert all(g["missing_features"] == [] for g in gaps)
    # The two image_generation reqs (features coerced to []) are satisfied
    # by the offering — no CAPABILITY_UNSATISFIED for them
    unsatisfied = [g for g in gaps if g["code"] == "CAPABILITY_UNSATISFIED"]
    assert unsatisfied == []


@pytest.mark.asyncio
async def test_long_connection_name_credential_fits_column(c):
    """A 100-char connection name (valid per schema) previously built a
    112-char credential name and overflowed the String(100) column (500)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _anthropic_adapter_id(c, h)
    long_name = "N" * 100
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={
            "adapter_id": aid,
            "name": long_name,
            "credentials": {"api_key": "sk-test-long-name"},
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["name"] == long_name
    assert data["credential_id"] is not None

    # Same construction on the update path (fresh connection, then add creds)
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "M" * 100},
        headers=h,
    )
    conn_id = r2.json()["data"]["id"]
    r3 = await c.put(
        f"/api/v1/orgs/{oid}/provider-connections/{conn_id}",
        json={"credentials": {"api_key": "sk-test-upd"}},
        headers=h,
    )
    assert r3.status_code == 200, r3.text
    assert r3.json()["data"]["credential_id"] is not None


@pytest.mark.asyncio
async def test_update_connection_name_validated(c):
    """UpdateConnectionRequest must mirror create's name bounds — a >100-char
    or blank name previously reached the String(100) column and 500ed."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "NameBound"},
        headers=h,
    )
    conn_id = r.json()["data"]["id"]
    url = f"/api/v1/orgs/{oid}/provider-connections/{conn_id}"

    for bad in ("x" * 101, "x" * 300, "", "   "):
        r2 = await c.put(url, json={"name": bad}, headers=h)
        assert r2.status_code == 422, f"name={bad!r}: {r2.status_code}"

    r3 = await c.put(url, json={"name": "  Trimmed OK  "}, headers=h)
    assert r3.status_code == 200
    assert r3.json()["data"]["name"] == "Trimmed OK"


@pytest.mark.asyncio
async def test_cost_boundary_matches_numeric_column(c):
    """Numeric(10,6) max is 9999.999999 — exactly 10000 passed the old
    validator (v > 10000) then overflowed at insert (500), on both create
    and update paths."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    base = {
        "connection_id": conn_id,
        "capability_key": "image_generation",
        "model_name": "cost-bound",
    }
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={**base, "cost_per_call_usd": 10000},
        headers=h,
    )
    assert r.status_code == 422

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={**base, "cost_per_call_usd": 9999.999999},
        headers=h,
    )
    assert r2.status_code == 201, r2.text
    offering_id = r2.json()["data"]["id"]

    url = f"/api/v1/orgs/{oid}/provider-offerings/{offering_id}"
    r3 = await c.put(url, json={"cost_per_call_usd": 10000}, headers=h)
    assert r3.status_code == 422
    r4 = await c.put(url, json={"cost_per_call_usd": 9999.999999}, headers=h)
    assert r4.status_code == 200


# ── Credential key handling (rotation + fail-fast) ────────


def test_invalid_encryption_key_raises(monkeypatch):
    """An invalid-format CREDENTIAL_ENCRYPTION_KEY must fail fast — the old
    silent SHA-256 derivation switched the effective key and bricked every
    stored credential."""
    from app.config import settings as live_settings
    from app.core.crypto import encrypt_credentials
    from app.exceptions import AppError

    monkeypatch.setattr(live_settings, "credential_encryption_key", "not-a-fernet-key")
    with pytest.raises(AppError) as exc_info:
        encrypt_credentials({"api_key": "x"})
    assert exc_info.value.code == "CREDENTIAL_KEY_INVALID"


def test_key_rotation_round_trip(monkeypatch):
    """Comma-separated keys: primary encrypts, all decrypt — a token written
    under the old key still decrypts after the new key is prepended."""
    from cryptography.fernet import Fernet

    from app.config import settings as live_settings
    from app.core.crypto import decrypt_credentials, encrypt_credentials

    old_key = Fernet.generate_key().decode()
    new_key = Fernet.generate_key().decode()

    monkeypatch.setattr(live_settings, "credential_encryption_key", old_key)
    token_old = encrypt_credentials({"api_key": "sk-rotate"})

    # Rotate: new primary first, old key kept for decryption
    monkeypatch.setattr(
        live_settings, "credential_encryption_key", f"{new_key},{old_key}"
    )
    assert decrypt_credentials(token_old) == {"api_key": "sk-rotate"}
    token_new = encrypt_credentials({"api_key": "sk-rotate"})
    # New tokens use the primary — decryptable with the new key alone
    monkeypatch.setattr(live_settings, "credential_encryption_key", new_key)
    assert decrypt_credentials(token_new) == {"api_key": "sk-rotate"}


# ── Audit fixes (Issue #21 follow-up) ─────────────────────


@pytest.mark.asyncio
async def test_update_offering_validators_mirror_create(c):
    """UpdateOfferingRequest must enforce the same bounds as create —
    updates previously bypassed cost/model/features/limits validation
    (audit MEDIUM 13)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "mock-v1",
        },
        headers=h,
    )
    offering_id = r.json()["data"]["id"]
    url = f"/api/v1/orgs/{oid}/provider-offerings/{offering_id}"

    bad_bodies = [
        {"cost_per_call_usd": -1},
        {"cost_per_call_usd": 10_001},
        {"model_name": ""},
        {"model_name": "x" * 201},
        {"features": ["f"] * 21},
        {"features": ["x" * 65]},
        {"limits": {"note": "x" * 5001}},
    ]
    for body in bad_bodies:
        r2 = await c.put(url, json=body, headers=h)
        assert r2.status_code == 422, f"{body}: {r2.status_code}"

    # Valid partial update still works
    r3 = await c.put(url, json={"cost_per_call_usd": 0.05}, headers=h)
    assert r3.status_code == 200
    assert r3.json()["data"]["cost_per_call_usd"] == 0.05


# ── Partial-update null semantics (R16 LOW batch) ─────────


@pytest.mark.asyncio
async def test_update_offering_explicit_null_clears_cost(c):
    """exclude_unset semantics: explicit `"cost_per_call_usd": null` clears
    the value, an absent field leaves it unchanged — the old
    `if value is not None` guard made both a silent no-op."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "cost-null",
            "cost_per_call_usd": 1.25,
        },
        headers=h,
    )
    offering_id = r.json()["data"]["id"]
    url = f"/api/v1/orgs/{oid}/provider-offerings/{offering_id}"

    # Absent field: cost unchanged
    r2 = await c.put(url, json={}, headers=h)
    assert r2.status_code == 200
    assert r2.json()["data"]["cost_per_call_usd"] == 1.25

    # Explicit null: cost cleared
    r3 = await c.put(url, json={"cost_per_call_usd": None}, headers=h)
    assert r3.status_code == 200
    assert r3.json()["data"]["cost_per_call_usd"] is None

    # Explicit null on a NON-nullable column is ignored, not a 500
    r4 = await c.put(url, json={"model_name": None}, headers=h)
    assert r4.status_code == 200
    assert r4.json()["data"]["model_name"] == "cost-null"


@pytest.mark.asyncio
async def test_update_connection_credentials_null_detaches_and_deletes(c):
    """Explicit `"credentials": null` detaches the credential AND deletes
    the org credential row (it belongs to this connection); an absent field
    leaves it unchanged; `{}` is a meaningless credential dict → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _anthropic_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={
            "adapter_id": aid,
            "name": "Detach",
            "credentials": {"api_key": "sk-detach-me"},
        },
        headers=h,
    )
    data = r.json()["data"]
    conn_id = data["id"]
    cred_id = data["credential_id"]
    assert cred_id is not None
    url = f"/api/v1/orgs/{oid}/provider-connections/{conn_id}"

    # Absent field: credential untouched
    r2 = await c.put(url, json={"name": "Detach 2"}, headers=h)
    assert r2.status_code == 200
    assert r2.json()["data"]["credential_id"] == cred_id

    # Empty dict: 422 (meaningless — null is the detach spelling)
    r3 = await c.put(url, json={"credentials": {}}, headers=h)
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "EMPTY_CREDENTIALS"

    # Explicit null: detached AND the credential row is gone
    r4 = await c.put(url, json={"credentials": None}, headers=h)
    assert r4.status_code == 200
    assert r4.json()["data"]["credential_id"] is None

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.provider import OrgCredential

    async with AsyncSessionLocal() as db:
        row = await db.execute(select(OrgCredential).where(OrgCredential.id == cred_id))
        assert row.scalar_one_or_none() is None

    # Detaching an already-credential-less connection is an idempotent no-op
    r5 = await c.put(url, json={"credentials": None}, headers=h)
    assert r5.status_code == 200
    assert r5.json()["data"]["credential_id"] is None


@pytest.mark.asyncio
async def test_cost_rounding_boundary_and_nan_rejected(c):
    """R18: [9999.9999995, 10000) ROUNDS to 10000.000000 in Numeric(10,6) and
    still overflowed; NaN passed both comparisons and later crashed Decimal
    sorts. Both must 422 at the schema."""
    import pydantic

    from app.schemas.provider import CreateOfferingRequest, UpdateOfferingRequest

    h, _ = await _auth(c)
    oid = await _org(c, h)
    conn_id = await _connection(c, h, oid)
    # Rounding boundary over the wire (valid JSON):
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "boundary-model",
            "cost_per_call_usd": 9999.9999999,
        },
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]
    # NaN/inf are not valid JSON — standard clients cannot send them, but a
    # non-standard serializer could; the validator itself must reject them
    for bad in (float("nan"), float("inf")):
        with pytest.raises(pydantic.ValidationError):
            CreateOfferingRequest(
                connection_id=conn_id,
                capability_key="image_generation",
                model_name="m",
                cost_per_call_usd=bad,
            )
        with pytest.raises(pydantic.ValidationError):
            UpdateOfferingRequest(cost_per_call_usd=bad)
    # Exact max still accepted
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "max-cost-model",
            "cost_per_call_usd": 9999.999999,
        },
        headers=h,
    )
    assert r.status_code == 201, r.text


@pytest.mark.asyncio
async def test_create_connection_empty_credentials_422(c):
    """R18: {} was silently swallowed on create while update 422s — the
    create path now matches (EMPTY_CREDENTIALS)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "EmptyCreds", "credentials": {}},
        headers=h,
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "EMPTY_CREDENTIALS"


@pytest.mark.asyncio
async def test_non_string_feature_entries_flagged_not_dropped(c):
    """R18: non-string entries INSIDE a features list were silently dropped,
    letting the requirement pass against any offering — now flagged as
    MALFORMED_REQUIREMENT while still not crashing."""
    from app.core.database import AsyncSessionLocal
    from app.services.provider import ProviderService

    h, _ = await _auth(c)
    oid = await _org(c, h)
    async with AsyncSessionLocal() as db:
        svc = ProviderService(db)
        gaps = await svc.check_capabilities(
            oid, [{"capability": "image_generation", "features": [123, 456]}]
        )
    codes = [g["code"] for g in gaps]
    assert "MALFORMED_REQUIREMENT" in codes, gaps


@pytest.mark.asyncio
async def test_connection_and_offering_nul_rejected(c):
    """R63: connection name / offering model_name (VARCHAR) and offering
    features (JSONB) accepted NUL -> 500 at flush. All 422 now."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)

    # connection name with NUL
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "conn" + chr(0) + "x"},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]

    # a clean connection, then offering with NUL model_name / features
    conn = (await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "clean"},
        headers=h,
    )).json()["data"]["id"]

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={"connection_id": conn, "capability_key": "image_generation",
              "model_name": "m" + chr(0) + "v"},
        headers=h,
    )
    assert r2.status_code == 422, r2.text[:200]

    r3 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={"connection_id": conn, "capability_key": "image_generation",
              "model_name": "ok", "features": ["hi" + chr(0) + "res"]},
        headers=h,
    )
    assert r3.status_code == 422, r3.text[:200]


@pytest.mark.asyncio
async def test_connection_config_nul_rejected_not_500(c):
    """R70: connection.config / offering.limits are open JSONB dicts whose
    validators only ran reject_deep_json — never reject_ctrl_json. A NUL
    smuggled into a value (valid-JSON \\u0000 escape → real NUL) reached the
    JSONB write and crashed asyncpg (22P05 → 500). Must be a clean 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)
    nul = chr(0)

    # config NUL on create
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": aid, "name": "x", "config": {"endpoint": "a" + nul + "b"}},
        headers=h,
    )
    assert r.status_code == 422, r.text[:200]

    # config NUL on update
    conn_id = await _connection(c, h, oid)
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/provider-connections/{conn_id}",
        json={"config": {"endpoint": "a" + nul + "b"}},
        headers=h,
    )
    assert r2.status_code == 422, r2.text[:200]

    # limits NUL on offering create
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "ok",
            "limits": {"note": "a" + nul + "b"},
        },
        headers=h,
    )
    assert r3.status_code == 422, r3.text[:200]

    # Control: clean config/limits still accepted
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "ok2",
            "limits": {"max_resolution": "2048x2048"},
        },
        headers=h,
    )
    assert r4.status_code == 201, r4.text[:200]


@pytest.mark.asyncio
async def test_connection_config_and_limits_nonfinite_rejected_not_500(c):
    """R73: config/limits are open JSONB dicts — a NaN/Infinity float (stdlib
    json.loads accepts the token) passed the size/depth/ctrl checks and 500'd
    at the JSONB write (22P02). Validators now screen non-finite floats → 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    aid = await _mock_adapter_id(c, h)
    hj = {**h, "Content-Type": "application/json"}

    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        content=('{"adapter_id":"%s","name":"x","config":{"rate": NaN}}' % aid).encode(),
        headers=hj,
    )
    assert r.status_code == 422, r.text[:150]

    conn_id = await _connection(c, h, oid)
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        content=(
            '{"connection_id":"%s","capability_key":"image_generation",'
            '"model_name":"m","limits":{"max": Infinity}}' % conn_id
        ).encode(),
        headers=hj,
    )
    assert r2.status_code == 422, r2.text[:150]

    # Control: finite limits still accepted
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/provider-offerings",
        json={
            "connection_id": conn_id,
            "capability_key": "image_generation",
            "model_name": "ok",
            "limits": {"max_resolution": "2048x2048", "throughput": 12.5},
        },
        headers=h,
    )
    assert r3.status_code == 201, r3.text[:150]
