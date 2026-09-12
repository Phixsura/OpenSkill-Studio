"""R437: provider check_capabilities — untrusted-manifest hardening + gap logic.

check_capabilities gates pack installation against an org's active provider
offerings. Manifests are attacker-controlled (public packs), so every
type-broken entry must become a MALFORMED_REQUIREMENT gap, never a 500, and
a feature must never silently vanish (weakening the gate).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
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
        email=f"r437-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R437",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(owner)
    await db.flush()
    o = await OrgService(db).create(
        name=f"R437 {uuid.uuid4().hex[:5]}",
        slug=f"r437-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _offering(db, org_id, capability, features, *, conn_status="active", active=True):
    from app.models.provider import (
        ProviderAdapter,
        ProviderConnection,
        ProviderModelOffering,
    )

    adapter = ProviderAdapter(key=f"mock-{uuid.uuid4().hex[:8]}", name="Mock")
    db.add(adapter)
    await db.flush()
    conn = ProviderConnection(org_id=org_id, adapter_id=adapter.id, name="c", status=conn_status)
    db.add(conn)
    await db.flush()
    off = ProviderModelOffering(
        connection_id=conn.id,
        capability_key=capability,
        model_name="m",
        features=features,
        is_active=active,
    )
    db.add(off)
    await db.flush()
    return off


def _codes(gaps):
    return [g["code"] for g in gaps]


async def test_check_capabilities_satisfaction_r437(db):
    from app.services.provider import ProviderService

    org = await _org(db)
    svc = ProviderService(db)
    await _offering(db, org.id, "image_generation", ["upscale", "hd"])

    # exact + subset feature requirements are satisfied → no gaps
    assert await svc.check_capabilities(org.id, [{"capability": "image_generation"}]) == []
    assert (
        await svc.check_capabilities(
            org.id, [{"capability": "image_generation", "features": ["upscale"]}]
        )
        == []
    )
    assert (
        await svc.check_capabilities(
            org.id, [{"capability": "image_generation", "features": ["upscale", "hd"]}]
        )
        == []
    )

    # a feature the offering lacks → CAPABILITY_UNSATISFIED with the missing set
    gaps = await svc.check_capabilities(
        org.id, [{"capability": "image_generation", "features": ["upscale", "4k"]}]
    )
    assert _codes(gaps) == ["CAPABILITY_UNSATISFIED"]
    assert gaps[0]["missing_features"] == ["4k", "upscale"]

    # an entirely unknown capability → unsatisfied
    gaps2 = await svc.check_capabilities(org.id, [{"capability": "video_generation"}])
    assert _codes(gaps2) == ["CAPABILITY_UNSATISFIED"]


async def test_check_capabilities_scoping_r437(db):
    from app.services.provider import ProviderService

    org = await _org(db)
    other = await _org(db)
    svc = ProviderService(db)

    # an offering in ANOTHER org must not satisfy this org
    await _offering(db, other.id, "image_generation", ["upscale"])
    assert _codes(await svc.check_capabilities(org.id, [{"capability": "image_generation"}])) == [
        "CAPABILITY_UNSATISFIED"
    ]

    # an INACTIVE offering / INACTIVE connection does not satisfy
    await _offering(db, org.id, "image_generation", ["upscale"], active=False)
    await _offering(db, org.id, "image_generation", ["upscale"], conn_status="disabled")
    assert _codes(await svc.check_capabilities(org.id, [{"capability": "image_generation"}])) == [
        "CAPABILITY_UNSATISFIED"
    ]

    # add an ACTIVE offering → now satisfied
    await _offering(db, org.id, "image_generation", ["upscale"])
    assert await svc.check_capabilities(org.id, [{"capability": "image_generation"}]) == []


async def test_check_capabilities_malformed_r437(db):
    from app.services.provider import ProviderService

    org = await _org(db)
    svc = ProviderService(db)

    # non-dict entry
    assert _codes(await svc.check_capabilities(org.id, ["not a dict"])) == ["MALFORMED_REQUIREMENT"]
    # non-string / empty capability
    assert _codes(await svc.check_capabilities(org.id, [{"capability": 123}])) == [
        "MALFORMED_REQUIREMENT"
    ]
    assert _codes(await svc.check_capabilities(org.id, [{"capability": ""}])) == [
        "MALFORMED_REQUIREMENT"
    ]
    # features not a list (a bare string would degrade to per-char subset match)
    assert _codes(
        await svc.check_capabilities(
            org.id, [{"capability": "image_generation", "features": "highres"}]
        )
    ) == ["MALFORMED_REQUIREMENT", "CAPABILITY_UNSATISFIED"]
    # a non-string feature INSIDE the list must be flagged, never silently
    # dropped (an int feature vanishing would let the requirement pass)
    await _offering(db, org.id, "image_generation", ["upscale"])
    gaps = await svc.check_capabilities(
        org.id, [{"capability": "image_generation", "features": ["upscale", 5]}]
    )
    assert "MALFORMED_REQUIREMENT" in _codes(gaps)
    # the valid part still matched (upscale present) so no UNSATISFIED for it
    assert "CAPABILITY_UNSATISFIED" not in _codes(gaps)
    # the detail counts and pluralizes the dropped entries (1 -> "entry")
    mal = next(g for g in gaps if g["code"] == "MALFORMED_REQUIREMENT")
    assert "1 non-string feature entry" in mal["detail"]
    # TWO non-string features -> plural "entries" and count 2
    gaps2 = await svc.check_capabilities(
        org.id, [{"capability": "image_generation", "features": ["upscale", 5, True]}]
    )
    mal2 = next(g for g in gaps2 if g["code"] == "MALFORMED_REQUIREMENT")
    assert "2 non-string feature entries" in mal2["detail"]

    # an empty requirement list → no gaps
    assert await svc.check_capabilities(org.id, []) == []
