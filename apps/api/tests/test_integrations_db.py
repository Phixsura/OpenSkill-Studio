"""Integration fabric P1 DB tests — catalog sync, connection CRUD + state
machine, write-only credentials, uniform-404 IDOR (read AND write)."""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select
from ulid import ULID

from app.core.security import hash_password
from app.exceptions import AppError
from app.integrations.services.connections import ConnectionService
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus
from app.models.user import User, UserRole, UserStatus


@pytest_asyncio.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db):
    u = User(
        email=f"intg-{uuid.uuid4().hex[:16]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="IntgTest",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _tenant(db, user):
    from app.controlplane.models import TenantStatus
    from app.controlplane.services import tenants as tenant_svc
    from app.controlplane.services.tenants import Actor

    return await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )


async def _org(db, user):
    tenant = await _tenant(db, user)
    org = Organization(
        name=f"Org {ULID()}",
        slug=f"org-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    await db.flush()
    return org


@pytest_asyncio.fixture
async def ctx(db):
    user = await _user(db)
    org = await _org(db, user)
    svc = ConnectionService(db)
    await svc.sync_provider_catalog()
    await db.flush()
    return {"db": db, "user": user, "org": org, "svc": svc}


# ── catalog ──


@pytest.mark.asyncio
async def test_catalog_sync_idempotent(ctx):
    svc = ctx["svc"]
    # Second sync changes nothing.
    assert await svc.sync_provider_catalog() == 0
    providers = await svc.list_providers()
    keys = {p.key for p in providers}
    assert {"generic_webhook", "generic_rest", "oneroster"} <= keys


# ── connection CRUD ──


async def _mk_conn(ctx, **over):
    kwargs = dict(
        provider_key="generic_rest",
        name=f"conn-{uuid.uuid4().hex[:8]}",
        config={},
        base_url="https://api.example.com/v1",
        created_by=ctx["user"].id,
    )
    kwargs.update(over)
    return await ctx["svc"].create(ctx["org"].id, **kwargs)


@pytest.mark.asyncio
async def test_create_pins_provider_version_and_starts_pending(ctx):
    conn = await _mk_conn(ctx)
    assert conn.status == "pending"
    assert conn.provider_version == 1
    assert conn.created_at is not None  # server default eagerly loaded


@pytest.mark.asyncio
async def test_create_unknown_provider_404(ctx):
    with pytest.raises(AppError) as e:
        await _mk_conn(ctx, provider_key="nope")
    assert e.value.code == "PROVIDER_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_duplicate_name_409(ctx):
    conn = await _mk_conn(ctx)
    with pytest.raises(AppError) as e:
        await _mk_conn(ctx, name=conn.name)
    assert e.value.code == "CONNECTION_NAME_TAKEN"


@pytest.mark.asyncio
async def test_create_private_base_url_blocked(ctx):
    with pytest.raises(AppError) as e:
        await _mk_conn(ctx, base_url="https://169.254.169.254/latest")
    assert e.value.code == "EGRESS_BLOCKED"


@pytest.mark.asyncio
async def test_config_schema_rejects_unknown_and_bad_types(ctx):
    with pytest.raises(AppError) as e:
        await _mk_conn(ctx, provider_key="oneroster", config={"bogus": 1})
    assert e.value.code == "CONNECTION_CONFIG_INVALID"
    # required token_url missing is in the details
    assert any("token_url" in d for d in (e.value.details or []))
    with pytest.raises(AppError) as e2:
        await _mk_conn(
            ctx,
            provider_key="oneroster",
            config={"token_url": "https://idp.example.com/token", "page_size": 9999},
        )
    assert any("page_size" in d for d in (e2.value.details or []))
    # bool is not an integer (R86 class: validate to true column bound)
    with pytest.raises(AppError):
        await _mk_conn(
            ctx,
            provider_key="oneroster",
            config={"token_url": "https://idp.example.com/token", "page_size": True},
        )


@pytest.mark.asyncio
async def test_admin_status_toggle_rules(ctx):
    svc, org = ctx["svc"], ctx["org"]
    conn = await _mk_conn(ctx)
    # pending -> disabled OK; disabled -> pending OK; direct "active" refused.
    await svc.update(org.id, conn.id, status="disabled")
    assert conn.status == "disabled"
    await svc.update(org.id, conn.id, status="pending")
    assert conn.status == "pending"
    with pytest.raises(AppError) as e:
        await svc.update(org.id, conn.id, status="active")
    assert e.value.code == "CONNECTION_STATUS_INVALID"


# ── uniform 404 (R88 class 2: read AND write) ──


@pytest.mark.asyncio
async def test_cross_tenant_uniform_404(ctx):
    db = ctx["db"]
    conn = await _mk_conn(ctx)
    other_user = await _user(db)
    other_org = await _org(db, other_user)
    svc = ctx["svc"]
    for call in (
        lambda: svc.get(other_org.id, conn.id),
        lambda: svc.update(other_org.id, conn.id, name="steal"),
        lambda: svc.delete(other_org.id, conn.id),
        lambda: svc.set_credential(
            other_org.id, conn.id, kind="api_key", values={"api_key": "x"}, expires_at=None
        ),
        lambda: svc.ping(other_org.id, conn.id),
    ):
        with pytest.raises(AppError) as e:
            await call()
        assert e.value.code == "CONNECTION_NOT_FOUND"
        assert e.value.status_code == 404


# ── credentials (write-only, rotate in place, error->pending reset) ──


@pytest.mark.asyncio
async def test_credential_roundtrip_encrypted_and_write_only(ctx):
    svc, org = ctx["svc"], ctx["org"]
    conn = await _mk_conn(ctx)
    cred = await svc.set_credential(
        org.id, conn.id, kind="api_key", values={"api_key": "sk-secret-1"}, expires_at=None
    )
    assert cred.rotated_at is not None
    assert "sk-secret-1" not in cred.ciphertext  # encrypted at rest
    # Decrypt path (what a connector sees via ConnCtx.get_secret)
    loader = await svc._secret_loader(conn.id)
    assert (await loader())["api_key"] == "sk-secret-1"
    # Rotation replaces in place — same row id, new ciphertext.
    cred2 = await svc.set_credential(
        org.id, conn.id, kind="api_key", values={"api_key": "sk-secret-2"}, expires_at=None
    )
    assert cred2.id == cred.id
    assert (await loader())["api_key"] == "sk-secret-2"


@pytest.mark.asyncio
async def test_credential_bad_kind_and_oversize_rejected(ctx):
    svc, org = ctx["svc"], ctx["org"]
    conn = await _mk_conn(ctx)
    with pytest.raises(AppError) as e:
        await svc.set_credential(org.id, conn.id, kind="magic", values={"k": "v"}, expires_at=None)
    assert e.value.code == "CREDENTIAL_KIND_INVALID"
    with pytest.raises(AppError) as e2:
        await svc.set_credential(
            org.id, conn.id, kind="api_key", values={"k": "v" * 5000}, expires_at=None
        )
    assert e2.value.code == "CREDENTIAL_VALUE_INVALID"


@pytest.mark.asyncio
async def test_replacing_credentials_reopens_errored_connection(ctx):
    svc, org = ctx["svc"], ctx["org"]
    conn = await _mk_conn(ctx)
    conn.status = "error"
    await svc.set_credential(
        org.id, conn.id, kind="api_key", values={"api_key": "fresh"}, expires_at=None
    )
    assert conn.status == "pending"


# ── health state machine ──


@pytest.mark.asyncio
async def test_ping_success_activates_and_failure_degrades(ctx, monkeypatch):
    svc, org = ctx["svc"], ctx["org"]
    # generic_webhook ping only re-screens base_url — a clean success path.
    conn = await _mk_conn(ctx, provider_key="generic_webhook", base_url=None, config={})
    await svc.ping(org.id, conn.id)
    assert conn.status == "active"
    assert conn.health["consecutive_failures"] == 0

    # Force failures through the connector registry.
    from app.integrations import registry

    class Boom:
        key = "generic_webhook"
        capabilities = frozenset({"events.deliver"})

        async def ping(self, ctx):
            raise AppError("CONNECTION_PING_FAILED", "down", 422)

    monkeypatch.setitem(registry.CONNECTORS, "generic_webhook", Boom())
    for _ in range(3):
        with pytest.raises(AppError):
            await svc.ping(org.id, conn.id)
    assert conn.status == "degraded"
    assert conn.health["consecutive_failures"] == 3

    # Two consecutive auth rejections park the connection in error.
    class AuthBoom(Boom):
        async def ping(self, ctx):
            raise AppError("CONNECTION_AUTH_REJECTED", "401", 422)

    monkeypatch.setitem(registry.CONNECTORS, "generic_webhook", AuthBoom())
    for _ in range(2):
        with pytest.raises(AppError):
            await svc.ping(org.id, conn.id)
    assert conn.status == "error"


# ── R13: explicit provider-version upgrade (ADR §19) ──


@pytest.mark.asyncio
async def test_connection_upgrade_revalidates(ctx):
    from app.integrations.models import IntegrationProvider

    svc, org, db = ctx["svc"], ctx["org"], ctx["db"]
    conn = await _mk_conn(
        ctx,
        provider_key="oneroster",
        config={"token_url": "https://idp.example.com/token", "page_size": 50},
    )
    assert conn.provider_version == 1
    # Idempotent when already current.
    same = await svc.upgrade(org.id, conn.id)
    assert same.provider_version == 1

    provider = (
        await db.execute(
            select(IntegrationProvider).where(IntegrationProvider.key == "oneroster")
        )
    ).scalars().first()
    # Catalog publishes v2 with a TIGHTER schema the stored config violates.
    provider.version = 2
    provider.config_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["token_url"],
        "properties": {
            "token_url": {"type": "string", "maxLength": 500},
            "page_size": {"type": "integer", "minimum": 10, "maximum": 20},
        },
    }
    await db.flush()
    with pytest.raises(AppError) as e:
        await svc.upgrade(org.id, conn.id)  # page_size 50 > new max 20
    assert e.value.code == "CONNECTION_CONFIG_INVALID"
    assert conn.provider_version == 1  # never silently bumped
    # Fix the config -> upgrade succeeds.
    await svc.update(
        org.id, conn.id,
        config={"token_url": "https://idp.example.com/token", "page_size": 15},
    )
    upgraded = await svc.upgrade(org.id, conn.id)
    assert upgraded.provider_version == 2
    # Restore catalog row for sibling tests.
    await svc.sync_provider_catalog()
    await db.commit()
