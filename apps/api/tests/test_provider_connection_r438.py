"""R438: provider connection/offering creation — credential + limit + taxonomy
guards. create_connection handles credentials (R3: no cred fields in config)
and gates on tenant status; create_offering enforces the closed capability
vocabulary.

Documented EQUIVALENT mutants (adjudicated): the 404->405 / 422->423 raises
are HTTP status-class swaps; L127 name[:88] -> [:89] is a ±1 truncation
bound on the credential-name prefix (String(100) column).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.provider import ProviderAdapter
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _org(db):
    from app.services.organization import OrgService

    owner = User(
        email=f"r438-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R438",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    await db.flush()
    o = await OrgService(db).create(
        name=f"R438 {uuid.uuid4().hex[:5]}",
        slug=f"r438-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o, owner


async def _adapter(db, credential_fields=None, is_active=True):
    a = ProviderAdapter(
        key=f"mock-{uuid.uuid4().hex[:8]}",
        name="Mock",
        credential_fields=credential_fields or ["api_key"],
        is_active=is_active,
    )
    db.add(a)
    await db.flush()
    return a


async def test_create_connection_guards_r438(db):
    from app.services.provider import ProviderService

    org, owner = await _org(db)
    svc = ProviderService(db)
    adapter = await _adapter(db, credential_fields=["api_key"])

    # unknown / inactive adapter → 404
    with pytest.raises(AppError) as e_na:
        await svc.create_connection(org.id, str(uuid.uuid4()), "c", {}, None, owner.id)
    assert e_na.value.code == "ADAPTER_NOT_FOUND"
    dead = await _adapter(db, is_active=False)
    with pytest.raises(AppError) as e_dead:
        await svc.create_connection(org.id, dead.id, "c", {}, None, owner.id)
    assert e_dead.value.code == "ADAPTER_NOT_FOUND"

    # R3: a credential field name smuggled into config → CREDENTIAL_IN_CONFIG
    with pytest.raises(AppError) as e_leak:
        await svc.create_connection(org.id, adapter.id, "c", {"api_key": "secret"}, None, owner.id)
    assert e_leak.value.code == "CREDENTIAL_IN_CONFIG"

    # an empty credentials dict is a client mistake → EMPTY_CREDENTIALS
    with pytest.raises(AppError) as e_empty:
        await svc.create_connection(org.id, adapter.id, "c", {}, {}, owner.id)
    assert e_empty.value.code == "EMPTY_CREDENTIALS"

    # an unknown credential field → UNKNOWN_CREDENTIAL_FIELD
    with pytest.raises(AppError) as e_unk:
        await svc.create_connection(
            org.id, adapter.id, "c", {}, {"api_key": "k", "wat": "x"}, owner.id
        )
    assert e_unk.value.code == "UNKNOWN_CREDENTIAL_FIELD"

    # a valid connection WITH credentials creates a credential row
    conn = await svc.create_connection(
        org.id, adapter.id, "Prod", {"region": "eu"}, {"api_key": "k"}, owner.id
    )
    assert conn.credential_id is not None
    # …and one WITHOUT credentials is allowed (credentials omitted, not {})
    conn2 = await svc.create_connection(org.id, adapter.id, "NoCred", {}, None, owner.id)
    assert conn2.credential_id is None


async def test_create_connection_suspended_tenant_r438(db):
    from app.controlplane.models.tenant import TenantAccount, TenantStatus
    from app.services.provider import ProviderService

    org, owner = await _org(db)
    svc = ProviderService(db)
    adapter = await _adapter(db)

    # a SUSPENDED tenant cannot add provider capacity
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.SUSPENDED
    await db.flush()
    with pytest.raises(AppError) as e_susp:
        await svc.create_connection(org.id, adapter.id, "c", {}, None, owner.id)
    assert e_susp.value.status_code in (402, 403, 409, 422, 423)  # tenant-blocked


async def test_create_offering_guards_r438(db):
    from app.services.provider import ProviderService

    org, owner = await _org(db)
    svc = ProviderService(db)
    adapter = await _adapter(db)
    conn = await svc.create_connection(org.id, adapter.id, "c", {}, None, owner.id)

    # unknown capability (closed taxonomy) → UNKNOWN_CAPABILITY
    with pytest.raises(AppError) as e_cap:
        await svc.create_offering(org.id, conn.id, "made_up_cap", "m", [], {}, None, "standard")
    assert e_cap.value.code == "UNKNOWN_CAPABILITY"

    # a known capability (seeded in the taxonomy) → offering created
    off = await svc.create_offering(
        org.id, conn.id, "image_generation", "sdxl", ["upscale"], {}, 0.01, "premium"
    )
    assert off.capability_key == "image_generation"
    assert off.features == ["upscale"]

    # a cross-org connection id → ownership check fails (not found)
    other_org, other_owner = await _org(db)
    with pytest.raises(AppError):
        await svc.create_offering(
            other_org.id, conn.id, "image_generation", "m", [], {}, None, "standard"
        )


async def test_connection_and_offering_limits_r438(db):
    from app.models.provider import ProviderConnection, ProviderModelOffering
    from app.services.provider import (
        MAX_CONNECTIONS_PER_ORG,
        MAX_OFFERINGS_PER_CONNECTION,
        ProviderService,
    )

    org, owner = await _org(db)
    svc = ProviderService(db)
    adapter = await _adapter(db)

    # fill the org to exactly MAX connections (direct inserts), then the next
    # create is rejected AT the bound (kills the `>= MAX` -> `> MAX` mutant)
    for _ in range(MAX_CONNECTIONS_PER_ORG):
        db.add(ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="c"))
    await db.flush()
    with pytest.raises(AppError) as e_conn:
        await svc.create_connection(org.id, adapter.id, "over", {}, None, owner.id)
    assert e_conn.value.code == "CONNECTION_LIMIT_REACHED"

    # offering limit: one connection filled to MAX offerings, next rejected
    org2, owner2 = await _org(db)
    conn = await ProviderService(db).create_connection(
        org2.id, adapter.id, "c", {}, None, owner2.id
    )
    for _ in range(MAX_OFFERINGS_PER_CONNECTION):
        db.add(
            ProviderModelOffering(
                connection_id=conn.id,
                capability_key="image_generation",
                model_name="m",
                features=[],
            )
        )
    await db.flush()
    with pytest.raises(AppError) as e_off:
        await svc.create_offering(
            org2.id, conn.id, "image_generation", "m", [], {}, None, "standard"
        )
    assert e_off.value.code == "OFFERING_LIMIT_REACHED"
