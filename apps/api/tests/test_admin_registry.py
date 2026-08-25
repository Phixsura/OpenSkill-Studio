"""Tests for admin pack-category CRUD hardening (R15 batch D).

Covers: parent cycle rejection, null-vs-absent parent_id semantics
(move-to-root), and sort_order bounds.
"""

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
    return f"adminreg-{uuid.uuid4().hex[:8]}@test.com"


async def _admin_headers(c):
    """Register a user, promote to admin via DB, return auth headers."""
    email = _email()
    await c.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "AdminPass123!", "display_name": "AdminReg"},
    )
    from sqlalchemy import select, update

    from app.core.database import AsyncSessionLocal
    from app.core.security import create_access_token
    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as db:
        await db.execute(update(User).where(User.email == email).values(role=UserRole.ADMIN))
        await db.commit()
        result = await db.execute(select(User).where(User.email == email))
        admin = result.scalar_one()
    return {"Authorization": f"Bearer {create_access_token(admin.id, admin.email, 'admin')}"}


async def _category(c, h, parent_id=None, **overrides):
    unique = uuid.uuid4().hex[:8]
    body = {
        "name": f"Cat {unique}",
        "slug": f"cat-{unique}",
        "parent_id": parent_id,
        "sort_order": 0,
        **overrides,
    }
    r = await c.post("/api/v1/admin/pack-categories", json=body, headers=h)
    assert r.status_code == 201, r.text
    return r.json()["data"]


# ── Cycle prevention ──────────────────────────────────────


@pytest.mark.asyncio
async def test_two_step_reparent_cycle_rejected(c):
    """A->B then B->A previously created a parent cycle: both nodes vanished
    from the root listing and mutually blocked deletion."""
    h = await _admin_headers(c)
    cat_a = await _category(c, h)
    cat_b = await _category(c, h, parent_id=cat_a["id"])

    r = await c.put(
        f"/api/v1/admin/pack-categories/{cat_a['id']}",
        json={"parent_id": cat_b["id"]},
        headers=h,
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "CATEGORY_CYCLE"


@pytest.mark.asyncio
async def test_deep_descendant_cycle_rejected(c):
    """Cycle detection walks the full ancestor chain, not just one hop:
    A->B->C then A.parent=C must also be rejected."""
    h = await _admin_headers(c)
    cat_a = await _category(c, h)
    cat_b = await _category(c, h, parent_id=cat_a["id"])
    cat_c = await _category(c, h, parent_id=cat_b["id"])

    r = await c.put(
        f"/api/v1/admin/pack-categories/{cat_a['id']}",
        json={"parent_id": cat_c["id"]},
        headers=h,
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "CATEGORY_CYCLE"


@pytest.mark.asyncio
async def test_direct_self_parent_still_rejected(c):
    h = await _admin_headers(c)
    cat = await _category(c, h)
    r = await c.put(
        f"/api/v1/admin/pack-categories/{cat['id']}",
        json={"parent_id": cat["id"]},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_valid_reparent_to_sibling_tree_ok(c):
    """Re-parenting to an unrelated category still works."""
    h = await _admin_headers(c)
    cat_a = await _category(c, h)
    cat_b = await _category(c, h)
    r = await c.put(
        f"/api/v1/admin/pack-categories/{cat_a['id']}",
        json={"parent_id": cat_b["id"]},
        headers=h,
    )
    assert r.status_code == 200, r.text
    assert r.json()["data"]["parent_id"] == cat_b["id"]


# ── null vs absent parent_id ──────────────────────────────


@pytest.mark.asyncio
async def test_explicit_null_parent_moves_to_root(c):
    """PATCH {"parent_id": null} must clear the parent (move to root) — the
    old exclude_none dump made null indistinguishable from absent, so a
    child could never be detached."""
    h = await _admin_headers(c)
    parent = await _category(c, h)
    child = await _category(c, h, parent_id=parent["id"])
    assert child["parent_id"] == parent["id"]

    r = await c.put(
        f"/api/v1/admin/pack-categories/{child['id']}",
        json={"parent_id": None},
        headers=h,
    )
    assert r.status_code == 200, r.text
    assert r.json()["data"]["parent_id"] is None


@pytest.mark.asyncio
async def test_absent_parent_id_leaves_parent_unchanged(c):
    """A body without parent_id must NOT touch the existing parent."""
    h = await _admin_headers(c)
    parent = await _category(c, h)
    child = await _category(c, h, parent_id=parent["id"])

    r = await c.put(
        f"/api/v1/admin/pack-categories/{child['id']}",
        json={},
        headers=h,
    )
    assert r.status_code == 200, r.text
    assert r.json()["data"]["parent_id"] == parent["id"]

    # Updating an unrelated field also leaves the parent alone
    r2 = await c.put(
        f"/api/v1/admin/pack-categories/{child['id']}",
        json={"sort_order": 5},
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["parent_id"] == parent["id"]
    assert r2.json()["data"]["sort_order"] == 5


# ── sort_order bounds ─────────────────────────────────────


@pytest.mark.asyncio
async def test_sort_order_bounded_create_and_update(c):
    """sort_order past int32 (2**40) previously reached the Integer column
    and 500ed with asyncpg integer-out-of-range."""
    h = await _admin_headers(c)
    unique = uuid.uuid4().hex[:8]
    r = await c.post(
        "/api/v1/admin/pack-categories",
        json={"name": f"Big {unique}", "slug": f"big-{unique}", "sort_order": 2**40},
        headers=h,
    )
    assert r.status_code == 422

    r2 = await c.post(
        "/api/v1/admin/pack-categories",
        json={"name": f"Neg {unique}", "slug": f"neg-{unique}", "sort_order": -1},
        headers=h,
    )
    assert r2.status_code == 422

    cat = await _category(c, h)
    r3 = await c.put(
        f"/api/v1/admin/pack-categories/{cat['id']}",
        json={"sort_order": 2**40},
        headers=h,
    )
    assert r3.status_code == 422

    r4 = await c.put(
        f"/api/v1/admin/pack-categories/{cat['id']}",
        json={"sort_order": 100000},
        headers=h,
    )
    assert r4.status_code == 200
    assert r4.json()["data"]["sort_order"] == 100000
