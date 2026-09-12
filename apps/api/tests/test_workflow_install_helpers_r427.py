"""R427: workflow-installation diff + upgrade binding-validity gate.

_diff_definitions drives the upgrade preview; _binding_still_valid (R73) is
the gate that drops a confirmed binding whose offering no longer satisfies a
changed step — preventing a deferred mid-run NO_ELIGIBLE_PROVIDER.
"""

import uuid

from ulid import ULID

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.services.workflow_installation import WorkflowInstallationService as Wi


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


def test_diff_definitions_r427():
    current = {
        "steps": [{"id": "a", "x": 1}, {"id": "b", "x": 1}, {"id": "c", "x": 1}],
        "inputs": [{"key": "k1", "v": 1}, {"key": "k2", "v": 1}],
        "edges": [{"id": "e1"}, {"id": "e2"}],
    }
    target = {
        "steps": [{"id": "b", "x": 1}, {"id": "c", "x": 2}, {"id": "d", "x": 1}],
        "inputs": [{"key": "k2", "v": 2}, {"key": "k3", "v": 1}],
        "edges": [{"id": "e2"}, {"id": "e3"}, {"id": "e4"}],
    }
    d = Wi._diff_definitions(current, target)
    # a removed, d added, c changed (x differs), b unchanged
    assert d["steps"]["added"] == ["d"]
    assert d["steps"]["removed"] == ["a"]
    assert d["steps"]["changed"] == ["c"]
    # k1 removed, k3 added, k2 changed
    assert d["inputs"]["added"] == ["k3"]
    assert d["inputs"]["removed"] == ["k1"]
    assert d["inputs"]["changed"] == ["k2"]
    # edges: e3,e4 added (2); e1 removed (1)
    assert d["edges"]["added_count"] == 2
    assert d["edges"]["removed_count"] == 1
    # an IDENTICAL step is not "changed"
    same = Wi._diff_definitions(current, current)
    assert same["steps"]["changed"] == []
    assert same["edges"]["added_count"] == 0


async def _conn(db, org_id, status="active"):
    from app.models.provider import ProviderAdapter, ProviderConnection

    adapter = ProviderAdapter(key=f"mock-{str(ULID()).lower()}", name="Mock")
    db.add(adapter)
    await db.flush()
    c = ProviderConnection(org_id=org_id, adapter_id=adapter.id, name="conn", status=status)
    db.add(c)
    await db.flush()
    return c


async def _offering(db, conn_id, capability="image_generation", features=None, is_active=True):
    from app.models.provider import ProviderModelOffering

    o = ProviderModelOffering(
        connection_id=conn_id, capability_key=capability, model_name="m",
        features=features or [], is_active=is_active,
    )
    db.add(o)
    await db.flush()
    return o


def _binding(offering_id):
    from app.models.workflow_run import WorkflowStepBinding

    return WorkflowStepBinding(
        org_id="o-1", installation_id="i-1", step_id="s1",
        binding_mode="offering", offering_id=offering_id,
    )


async def _user(db):
    u = User(email=f"r427-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name="R427", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org(db):
    from app.services.organization import OrgService

    owner = await _user(db)
    o = await OrgService(db).create(name=f"R427 {uuid.uuid4().hex[:5]}",
                                    slug=f"r427-{uuid.uuid4().hex[:10]}",
                                    description=None, created_by=owner.id)
    await db.flush()
    return o


async def test_binding_still_valid_gate_r427(db):
    org = await _org(db)
    org_id = org.id
    svc = Wi(db)
    step = {"capability": "image_generation", "required_features": ["upscale"]}

    conn = await _conn(db, org_id)
    good = await _offering(db, conn.id, features=["upscale", "hd"])
    # all conditions met → valid
    assert await svc._binding_still_valid(_binding(good.id), org_id, step) is True

    # no offering_id (SET NULL after offering deleted) → invalid
    assert await svc._binding_still_valid(_binding(None), org_id, step) is False

    # inactive offering → invalid
    inactive = await _offering(db, conn.id, features=["upscale"], is_active=False)
    assert await svc._binding_still_valid(_binding(inactive.id), org_id, step) is False

    # wrong capability → invalid
    wrongcap = await _offering(db, conn.id, capability="video_generation", features=["upscale"])
    assert await svc._binding_still_valid(_binding(wrongcap.id), org_id, step) is False

    # missing a newly-required feature → invalid (R73 core: capability alone
    # is not enough)
    nofeat = await _offering(db, conn.id, features=["hd"])  # no "upscale"
    assert await svc._binding_still_valid(_binding(nofeat.id), org_id, step) is False

    # a cross-ORG connection → invalid (the offering's connection must belong
    # to this org)
    other_org = await _org(db)
    other_conn = await _conn(db, other_org.id)
    other_off = await _offering(db, other_conn.id, features=["upscale"])
    assert await svc._binding_still_valid(_binding(other_off.id), org_id, step) is False

    # an INACTIVE connection → invalid
    dead_conn = await _conn(db, org_id, status="disabled")
    dead_off = await _offering(db, dead_conn.id, features=["upscale"])
    assert await svc._binding_still_valid(_binding(dead_off.id), org_id, step) is False

    # a step with NO required_features accepts any active same-capability offering
    step_nofeat = {"capability": "image_generation", "required_features": []}
    bare = await _offering(db, conn.id, features=[])
    assert await svc._binding_still_valid(_binding(bare.id), org_id, step_nofeat) is True
