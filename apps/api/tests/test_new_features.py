"""Integration tests for 7 untested features — reviews, analytics, notifications,
certificates, approval workflow, categories, LTI."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"feat-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app

    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager

    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Tester"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"Org-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


async def _skill(c, h, oid, name="Test Skill"):
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": f"Cat-{uuid.uuid4().hex[:4]}"}, headers=h)).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/skills", json={
        "name": name, "description": "d" * 10, "difficulty": "beginner", "category_id": cat,
    }, headers=h)
    return r.json()["data"]["id"]


async def _published_public_pack(c, h, oid, pack_name="Pub Pack", skill_name="Pub Skill"):
    """Create a published, public pack and return its id."""
    pid = (await c.post(f"/api/v1/orgs/{oid}/packs", json={
        "name": pack_name, "visibility": "public",
    }, headers=h)).json()["data"]["id"]
    sid = await _skill(c, h, oid, skill_name)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/skills", json={"skill_id": sid}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/releases", json={"version": "1.0.0"}, headers=h)
    return pid


# ═══════════════ Pack Reviews (5 tests) ═══════════════


@pytest.mark.asyncio
async def test_create_review(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    r = await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={
        "rating": 5, "title": "Great pack!", "body": "Very useful.",
    }, headers=h)
    assert r.status_code == 201
    d = r.json()["data"]
    assert d["rating"] == 5
    assert d["title"] == "Great pack!"
    assert d["pack_id"] == pid


@pytest.mark.asyncio
async def test_list_reviews(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 4}, headers=h)

    r = await c.get(f"/api/v1/registry/packs/{pid}/reviews")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_delete_review(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    cr = await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 3}, headers=h)
    rid = cr.json()["data"]["id"]

    r = await c.delete(f"/api/v1/registry/packs/{pid}/reviews/{rid}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_duplicate_review_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 5}, headers=h)

    r = await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 3}, headers=h)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_review_updates_average(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 4}, headers=h)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}", headers=h)
    d = r.json()["data"]
    assert d["average_rating"] == 4.0
    assert d["review_count"] == 1


# ═══════════════ Analytics (2 tests) ═══════════════


@pytest.mark.asyncio
async def test_get_pack_analytics(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)

    r = await c.get(f"/api/v1/orgs/{oid}/packs/{pid}/analytics", headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert "install_count" in d
    assert "average_rating" in d
    assert "review_count" in d
    assert "installs_by_version" in d


@pytest.mark.asyncio
async def test_analytics_cross_org(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)
    pid = await _published_public_pack(c, h1, oid1)

    r = await c.get(f"/api/v1/orgs/{oid2}/packs/{pid}/analytics", headers=h2)
    assert r.status_code == 404


# ═══════════════ Notifications (3 tests) ═══════════════


@pytest.mark.asyncio
async def test_list_notifications(c):
    h, _ = await _auth(c)

    r = await c.get("/api/v1/notifications", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_mark_notification_read(c):
    h, u = await _auth(c)
    oid = await _org(c, h)

    # Insert a notification directly via DB
    from app.core.database import AsyncSessionLocal
    from app.models.notification import Notification

    async with AsyncSessionLocal() as session:
        n = Notification(
            user_id=u["id"],
            org_id=oid,
            type="test",
            title="Test Notification",
            body="Test body",
            data={},
        )
        session.add(n)
        await session.flush()
        nid = n.id
        await session.commit()

    r = await c.put(f"/api/v1/notifications/{nid}/read", headers=h)
    assert r.status_code == 200

    # Should no longer appear in unread list
    r2 = await c.get("/api/v1/notifications", headers=h)
    assert r2.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_publish_creates_notification(c):
    # User 1 creates a published public pack
    h1, _ = await _auth(c)
    oid1 = await _org(c, h1)
    pid = (await c.post(f"/api/v1/orgs/{oid1}/packs", json={
        "name": "Notif Pack", "visibility": "public",
    }, headers=h1)).json()["data"]["id"]
    sid = await _skill(c, h1, oid1, "Notif Skill")
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/skills", json={"skill_id": sid}, headers=h1)
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={
        "version": "1.0.0",
    }, headers=h1)

    # User 2 creates org2 and installs the pack
    h2, _ = await _auth(c)
    oid2 = await _org(c, h2)
    ir = await c.post(f"/api/v1/orgs/{oid2}/installations", json={"pack_id": pid}, headers=h2)
    assert ir.status_code == 201

    # User 1 publishes v2.0.0
    await c.post(f"/api/v1/orgs/{oid1}/packs/{pid}/releases", json={
        "version": "2.0.0", "changelog": "New features",
    }, headers=h1)

    # User 2 should have a notification about the update
    r = await c.get("/api/v1/notifications", headers=h2)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1
    titles = [n["title"] for n in r.json()["data"]]
    assert any("2.0.0" in t for t in titles)


# ═══════════════ Certificates (2 tests) ═══════════════


@pytest.mark.asyncio
async def test_certificate_issued_on_completion(c):
    h, u = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Cert Skill")

    # Create learning path
    pr = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Cert Path"}, headers=h)
    assert pr.status_code == 201
    path_id = pr.json()["data"]["id"]

    # Add skill item
    await c.post(f"/api/v1/orgs/{oid}/paths/{path_id}/items", json={
        "item_type": "skill", "skill_id": sid, "sort_order": 0, "required": True,
    }, headers=h)

    # Mark skill as completed via DB
    from app.core.database import AsyncSessionLocal
    from app.models.skill import ProgressStatus, SkillProgress

    async with AsyncSessionLocal() as session:
        sp = SkillProgress(
            org_id=oid,
            skill_id=sid,
            user_id=u["id"],
            status=ProgressStatus.COMPLETED,
        )
        session.add(sp)
        await session.commit()

    # Get progress — should trigger certificate issuance
    r = await c.get(f"/api/v1/orgs/{oid}/paths/{path_id}/my-progress", headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["pct"] == 100
    assert "certificate_number" in d


@pytest.mark.asyncio
async def test_certificate_public_verification(c):
    h, u = await _auth(c)
    oid = await _org(c, h)

    # Create a certificate directly in the DB
    import uuid as _uuid

    from app.core.database import AsyncSessionLocal
    from app.models.certificate import Certificate

    # We need a path_id — create a learning path
    pr = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Verify Path"}, headers=h)
    path_id = pr.json()["data"]["id"]

    cert_number = str(_uuid.uuid4())
    async with AsyncSessionLocal() as session:
        cert = Certificate(
            user_id=u["id"],
            path_id=path_id,
            org_id=oid,
            certificate_number=cert_number,
            data={"user_name": "Tester", "path_name": "Verify Path", "org_name": "TestOrg"},
        )
        session.add(cert)
        await session.commit()

    # Public verification — no auth needed
    r2 = await c.get(f"/api/v1/certificates/{cert_number}")
    assert r2.status_code == 200
    d = r2.json()["data"]
    assert d["certificate_number"] == cert_number


# ═══════════════ Approval (3 tests) ═══════════════


async def _set_review_status(pack_id: str, status: str):
    """Set review_status on a pack via raw SQL to avoid session conflicts."""
    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE skill_packs SET review_status = :s WHERE id = :id"),
            {"s": status, "id": pack_id},
        )
        await session.commit()


@pytest.mark.asyncio
async def test_approve_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "Approve Pack")
    await _set_review_status(pid, "pending")

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/approve", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["review_status"] == "approved"


@pytest.mark.asyncio
async def test_reject_pack(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "Reject Pack")
    await _set_review_status(pid, "pending")

    r = await c.post(f"/api/v1/orgs/{oid}/packs/{pid}/reject", json={
        "reason": "Needs improvement",
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["review_status"] == "rejected"


@pytest.mark.asyncio
async def test_pending_pack_excluded_from_registry(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = uuid.uuid4().hex[:8]
    pid = await _published_public_pack(c, h, oid, f"Pending-{unique}")
    await _set_review_status(pid, "pending")

    # Clear registry cache so the search hits the DB
    from app.core.cache import cache_delete_pattern

    await cache_delete_pattern("registry:*")

    r = await c.get("/api/v1/registry/packs", params={"search": f"Pending-{unique}"})
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    assert pid not in ids


# ═══════════════ Categories (2 tests) ═══════════════


@pytest.mark.asyncio
async def test_list_categories(c):
    # Create pack categories via DB
    from app.core.database import AsyncSessionLocal
    from app.models.pack_category import PackCategory

    unique = uuid.uuid4().hex[:6]
    async with AsyncSessionLocal() as session:
        cat = PackCategory(
            name=f"AI Skills {unique}", slug=f"ai-skills-{unique}", sort_order=0,
        )
        session.add(cat)
        await session.commit()

    r = await c.get("/api/v1/registry/categories")
    assert r.status_code == 200
    slugs = [cat["slug"] for cat in r.json()["data"]]
    assert f"ai-skills-{unique}" in slugs


@pytest.mark.asyncio
async def test_filter_by_category(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    unique = uuid.uuid4().hex[:6]
    pid = await _published_public_pack(c, h, oid, f"CatFilter-{unique}")

    # Create category and assign pack to it via DB
    from app.core.database import AsyncSessionLocal
    from app.models.pack_category import PackCategory, PackCategoryAssignment

    cat_slug = f"cat-filter-{unique}"
    async with AsyncSessionLocal() as session:
        cat = PackCategory(
            name=f"Filter Cat {unique}", slug=cat_slug, sort_order=0,
        )
        session.add(cat)
        await session.flush()
        assignment = PackCategoryAssignment(pack_id=pid, category_id=cat.id)
        session.add(assignment)
        await session.commit()

    # Clear registry cache
    from app.core.cache import cache_delete_pattern

    await cache_delete_pattern("registry:*")

    r = await c.get("/api/v1/registry/packs", params={"category": cat_slug})
    assert r.status_code == 200
    ids = [p["id"] for p in r.json()["data"]]
    assert pid in ids


# ═══════════════ LTI (1 test) ═══════════════


@pytest.mark.asyncio
async def test_lti_config_coming_soon(c):
    r = await c.get("/api/v1/lti/config/some-pack-id")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["status"] == "coming_soon"
    assert d["pack_id"] == "some-pack-id"
