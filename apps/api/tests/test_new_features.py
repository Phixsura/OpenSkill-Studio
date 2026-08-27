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
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
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
    hr, _ = await _auth(c)  # reviewer (different user)

    r = await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={
        "rating": 5, "title": "Great pack!", "body": "Very useful.",
    }, headers=hr)
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
    hr, _ = await _auth(c)  # reviewer
    await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 4}, headers=hr)

    r = await c.get(f"/api/v1/registry/packs/{pid}/reviews")
    assert r.status_code == 200
    assert r.json()["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_delete_review(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    hr, _ = await _auth(c)  # reviewer
    cr = await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 3}, headers=hr)
    rid = cr.json()["data"]["id"]

    r = await c.delete(f"/api/v1/registry/packs/{pid}/reviews/{rid}", headers=hr)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_duplicate_review_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    hr, _ = await _auth(c)  # reviewer
    await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 5}, headers=hr)

    r = await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 3}, headers=hr)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_review_updates_average(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid)
    hr, _ = await _auth(c)  # reviewer
    await c.post(f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 4}, headers=hr)

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


# ═══════════════ Review Endpoints (4 tests) ═══════════════


@pytest.mark.asyncio
async def test_update_review(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "Update Review Pack")
    hr, _ = await _auth(c)  # reviewer
    cr = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews",
        json={"rating": 3},
        headers=hr,
    )
    rid = cr.json()["data"]["id"]

    r = await c.put(
        f"/api/v1/registry/packs/{pid}/reviews/{rid}",
        json={"rating": 5, "title": "Updated title"},
        headers=hr,
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["rating"] == 5
    assert d["title"] == "Updated title"


@pytest.mark.asyncio
async def test_reply_to_review(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "Reply Review Pack")

    # A different user creates the review (self-reviews are blocked)
    h2, _ = await _auth(c)
    cr = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews",
        json={"rating": 4, "title": "Good pack"},
        headers=h2,
    )
    rid = cr.json()["data"]["id"]

    # Pack owner replies to the review
    r = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews/{rid}/reply",
        json={"reply_text": "Thanks for the feedback!"},
        headers=h,
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["reply_text"] == "Thanks for the feedback!"
    assert d["reply_at"] is not None


@pytest.mark.asyncio
async def test_toggle_helpful(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "Helpful Review Pack")
    hr, _ = await _auth(c)  # reviewer
    cr = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews",
        json={"rating": 5, "title": "Excellent"},
        headers=hr,
    )
    rid = cr.json()["data"]["id"]

    # Toggle helpful ON (pack owner votes on the review)
    r = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews/{rid}/helpful",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["helpful_count"] == 1

    # Toggle helpful OFF
    r2 = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews/{rid}/helpful",
        headers=h,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["helpful_count"] == 0


@pytest.mark.asyncio
async def test_get_review_stats(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _published_public_pack(c, h, oid, "Stats Review Pack")
    hr, _ = await _auth(c)  # reviewer
    await c.post(
        f"/api/v1/registry/packs/{pid}/reviews",
        json={"rating": 4},
        headers=hr,
    )

    r = await c.get(f"/api/v1/registry/packs/{pid}/reviews/stats")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["average"] == 4.0
    assert d["total"] == 1
    assert d["distribution"]["4"] == 1


# ═══════════════ LTI (1 test) ═══════════════


@pytest.mark.asyncio
async def test_lti_config_coming_soon(c):
    r = await c.get("/api/v1/lti/config/some-pack-id")
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["status"] == "coming_soon"
    assert d["pack_id"] == "some-pack-id"


# ═══════════════ #13: locally_modified set on update (3 tests) ═══════════════


@pytest.mark.asyncio
async def test_locally_modified_set_on_skill_update(c):
    """When a skill installed from a pack is updated, locally_modified must be True."""
    h, u = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Pack Skill LM")

    # Simulate the skill having been installed from a pack by setting origin_pack_id
    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                "UPDATE skills SET origin_pack_id = 'fakePack00000000000000001' WHERE id = :id"
            ),
            {"id": sid},
        )
        await session.commit()

    # Update the skill — should set locally_modified = True
    r = await c.put(
        f"/api/v1/orgs/{oid}/skills/{sid}",
        json={"description": "Updated description"},
        headers=h,
    )
    assert r.status_code == 200

    # Verify locally_modified is now True
    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text("SELECT locally_modified FROM skills WHERE id = :id"),
            {"id": sid},
        )
        assert row.scalar_one() is True


@pytest.mark.asyncio
async def test_locally_modified_not_set_without_pack(c):
    """When a skill NOT from a pack is updated, locally_modified stays False."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Non-Pack Skill LM")

    r = await c.put(
        f"/api/v1/orgs/{oid}/skills/{sid}",
        json={"description": "Updated"},
        headers=h,
    )
    assert r.status_code == 200

    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text("SELECT locally_modified FROM skills WHERE id = :id"),
            {"id": sid},
        )
        assert row.scalar_one() is False


@pytest.mark.asyncio
async def test_locally_modified_set_on_exercise_update(c):
    """When an exercise installed from a pack is updated, locally_modified must be True."""
    h, u = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Ex Pack Skill")

    # Create an exercise
    er = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises",
        json={
            "title": "Ex1",
            "description": "desc",
            "type": "text_answer",
            "config": {},
            "max_score": 10,
        },
        headers=h,
    )
    assert er.status_code == 201
    eid = er.json()["data"]["id"]

    # Simulate pack origin
    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        await session.execute(
            text(
                "UPDATE exercises SET origin_pack_id = 'fakePack00000000000000001' WHERE id = :id"
            ),
            {"id": eid},
        )
        await session.commit()

    # Update the exercise
    r = await c.put(
        f"/api/v1/orgs/{oid}/exercises/{eid}",
        json={"title": "Updated Ex1"},
        headers=h,
    )
    assert r.status_code == 200

    # Verify
    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text("SELECT locally_modified FROM exercises WHERE id = :id"),
            {"id": eid},
        )
        assert row.scalar_one() is True


# ═══════════════ #19: Effective skills de-duplication (2 tests) ═══════════════


@pytest.mark.asyncio
async def test_effective_skills_deduplication(c):
    """A skill directly assigned AND in a learning path should appear only once."""
    h, u = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Eff Dedup Skill")

    # Create a cohort
    cr = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={"name": f"Cohort-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    assert cr.status_code == 201
    cohort_id = cr.json()["data"]["id"]

    # Direct-assign the skill to the cohort
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/skills",
        json={"skill_id": sid},
        headers=h,
    )
    assert r.status_code == 201

    # Create a learning path containing the same skill, publish it
    pr = await c.post(
        f"/api/v1/orgs/{oid}/paths",
        json={"name": "Eff Path"},
        headers=h,
    )
    assert pr.status_code == 201
    path_id = pr.json()["data"]["id"]

    await c.post(
        f"/api/v1/orgs/{oid}/paths/{path_id}/items",
        json={"item_type": "skill", "skill_id": sid, "sort_order": 0, "required": True},
        headers=h,
    )
    # Publish the path
    await c.put(
        f"/api/v1/orgs/{oid}/paths/{path_id}",
        json={"status": "published"},
        headers=h,
    )

    # Assign the path to the cohort
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths",
        json={"path_id": path_id},
        headers=h,
    )

    # Fetch effective skills — the skill should appear only once
    r = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/effective-skills",
        headers=h,
    )
    assert r.status_code == 200
    skill_ids = r.json()["data"]
    assert sid in skill_ids
    assert skill_ids.count(sid) == 1, "Duplicate skill detected in effective-skills"


@pytest.mark.asyncio
async def test_effective_skills_union(c):
    """Effective skills should include both directly assigned and path skills."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    s1 = await _skill(c, h, oid, "Direct Only Skill")
    s2 = await _skill(c, h, oid, "Path Only Skill")

    # Create cohort
    cr = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={"name": f"Union-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    cohort_id = cr.json()["data"]["id"]

    # Direct-assign s1
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/skills",
        json={"skill_id": s1},
        headers=h,
    )

    # Path with s2, published
    pr = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Union Path"}, headers=h)
    path_id = pr.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/paths/{path_id}/items",
        json={"item_type": "skill", "skill_id": s2, "sort_order": 0, "required": True},
        headers=h,
    )
    await c.put(f"/api/v1/orgs/{oid}/paths/{path_id}", json={"status": "published"}, headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths",
        json={"path_id": path_id},
        headers=h,
    )

    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/effective-skills", headers=h)
    assert r.status_code == 200
    skill_ids = r.json()["data"]
    assert s1 in skill_ids
    assert s2 in skill_ids


# ═══════════════ #21: Cohort path-level progress view (2 tests) ═══════════════


@pytest.mark.asyncio
async def test_cohort_path_progress_instructor_view(c):
    """Instructor can view per-learner progress on a path within a cohort."""
    h, u = await _auth(c)
    oid = await _org(c, h)
    sid = await _skill(c, h, oid, "Progress Skill")

    # Create path + item
    pr = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Prog Path"}, headers=h)
    path_id = pr.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/paths/{path_id}/items",
        json={"item_type": "skill", "skill_id": sid, "sort_order": 0, "required": True},
        headers=h,
    )
    await c.put(f"/api/v1/orgs/{oid}/paths/{path_id}", json={"status": "published"}, headers=h)

    # Create cohort, add a learner
    cr = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={"name": f"ProgCohort-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    cohort_id = cr.json()["data"]["id"]

    # Register a second user as learner
    h2, u2 = await _auth(c)
    # Add learner to org first
    from app.core.database import AsyncSessionLocal
    from app.models.organization import MemberStatus, OrgMember
    from app.models.organization import OrgRole as OrgRoleModel

    async with AsyncSessionLocal() as session:
        member = OrgMember(
            org_id=oid,
            user_id=u2["id"],
            role=OrgRoleModel.STUDENT,
            status=MemberStatus.ACTIVE,
        )
        session.add(member)
        await session.commit()

    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/members",
        json={"user_id": u2["id"], "role": "learner"},
        headers=h,
    )

    # Assign path to cohort
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths",
        json={"path_id": path_id},
        headers=h,
    )

    # Get cohort path progress as instructor
    r = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths/{path_id}/progress",
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert isinstance(data, list)
    # Should have at least the enrolled learner
    user_ids = [d["user_id"] for d in data]
    assert u2["id"] in user_ids
    # Each entry should have progress fields
    for entry in data:
        assert "completed" in entry
        assert "total_required" in entry
        assert "pct" in entry


@pytest.mark.asyncio
async def test_cohort_path_progress_non_instructor_denied(c):
    """Non-instructor members should not access cohort path progress."""
    h, u = await _auth(c)
    oid = await _org(c, h)

    # Create path + cohort as instructor
    pr = await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "Deny Path"}, headers=h)
    path_id = pr.json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/paths/{path_id}", json={"status": "published"}, headers=h)

    cr = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={"name": f"DenyCohort-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    cohort_id = cr.json()["data"]["id"]

    # Create a regular member (not instructor)
    h2, u2 = await _auth(c)
    from app.core.database import AsyncSessionLocal
    from app.models.organization import MemberStatus, OrgMember
    from app.models.organization import OrgRole as OrgRoleModel

    async with AsyncSessionLocal() as session:
        member = OrgMember(
            org_id=oid,
            user_id=u2["id"],
            role=OrgRoleModel.STUDENT,
            status=MemberStatus.ACTIVE,
        )
        session.add(member)
        await session.commit()

    r = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths/{path_id}/progress",
        headers=h2,
    )
    assert r.status_code == 403


# ═══════════════ #18: Direct + path assignments coexist (1 test) ═══════════════


@pytest.mark.asyncio
async def test_direct_and_path_assignments_coexist(c):
    """Direct cohort skill assignments and learning-path assignments coexist."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Two distinct skills
    s_direct = await _skill(c, h, oid, "Direct Assign Skill")
    s_path = await _skill(c, h, oid, "Path Assign Skill")

    # Create cohort and activate it
    cr = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={"name": f"Coexist-{uuid.uuid4().hex[:6]}"},
        headers=h,
    )
    assert cr.status_code == 201
    cohort_id = cr.json()["data"]["id"]
    ar = await c.put(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}",
        json={"status": "active"},
        headers=h,
    )
    assert ar.status_code == 200

    # 1) Directly assign s_direct to the cohort
    dr = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/skills",
        json={"skill_id": s_direct},
        headers=h,
    )
    assert dr.status_code == 201

    # 2) Create a learning path with s_path, publish it, assign to same cohort
    pr = await c.post(
        f"/api/v1/orgs/{oid}/paths",
        json={"name": "Coexist Path"},
        headers=h,
    )
    assert pr.status_code == 201
    path_id = pr.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/paths/{path_id}/items",
        json={"item_type": "skill", "skill_id": s_path, "sort_order": 0, "required": True},
        headers=h,
    )
    await c.put(
        f"/api/v1/orgs/{oid}/paths/{path_id}",
        json={"status": "published"},
        headers=h,
    )
    pra = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths",
        json={"path_id": path_id},
        headers=h,
    )
    assert pra.status_code == 201

    # Verify: GET cohort skills returns the directly assigned skill
    sr = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/skills",
        headers=h,
    )
    assert sr.status_code == 200
    direct_skill_ids = [a["skill_id"] for a in sr.json()["data"]]
    assert s_direct in direct_skill_ids

    # Verify: GET cohort paths returns the assigned path
    lpr = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/paths",
        headers=h,
    )
    assert lpr.status_code == 200
    path_ids = [p["path_id"] for p in lpr.json()["data"]]
    assert path_id in path_ids

    # Both coexist: effective-skills should contain both
    efr = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cohort_id}/effective-skills",
        headers=h,
    )
    assert efr.status_code == 200
    effective = efr.json()["data"]
    assert s_direct in effective
    assert s_path in effective


# ═══════════════ #29: Upgrade operation tests (2 tests) ═══════════════


@pytest.mark.asyncio
async def test_upgrade_clean(c):
    """Install v1.0.0, publish v1.1.0 with a new skill, upgrade, verify version."""
    h, u = await _auth(c)
    oid_pub = await _org(c, h)  # publisher org
    oid_con = await _org(c, h)  # consumer org (same user for simplicity)

    # Create pack with one skill, publish 1.0.0
    sid1 = await _skill(c, h, oid_pub, "Upgrade Skill A")
    pack_r = await c.post(
        f"/api/v1/orgs/{oid_pub}/packs",
        json={"name": f"UpgPack-{uuid.uuid4().hex[:6]}", "visibility": "public"},
        headers=h,
    )
    assert pack_r.status_code == 201
    pack_id = pack_r.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/skills",
        json={"skill_id": sid1},
        headers=h,
    )
    rel1 = await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert rel1.status_code == 201

    # Install in consumer org
    inst_r = await c.post(
        f"/api/v1/orgs/{oid_con}/installations",
        json={"pack_id": pack_id},
        headers=h,
    )
    assert inst_r.status_code == 201
    install_id = inst_r.json()["data"]["id"]
    assert inst_r.json()["data"]["installed_version"] == "1.0.0"

    # Publish v1.1.0 with a NEW skill added to the pack
    sid2 = await _skill(c, h, oid_pub, "Upgrade Skill B")
    await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/skills",
        json={"skill_id": sid2},
        headers=h,
    )
    rel2 = await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/releases",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert rel2.status_code == 201

    # Upgrade
    upg = await c.post(
        f"/api/v1/orgs/{oid_con}/installations/{install_id}/upgrade",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert upg.status_code == 200
    assert upg.json()["data"]["installed_version"] == "1.1.0"


@pytest.mark.asyncio
async def test_upgrade_locally_modified_skipped(c):
    """Locally modified skills are NOT overwritten during upgrade."""
    h, u = await _auth(c)
    oid_pub = await _org(c, h)
    oid_con = await _org(c, h)

    # Create pack with one skill, publish 1.0.0
    sid = await _skill(c, h, oid_pub, "LM Upgrade Skill")
    pack_r = await c.post(
        f"/api/v1/orgs/{oid_pub}/packs",
        json={"name": f"LMPack-{uuid.uuid4().hex[:6]}", "visibility": "public"},
        headers=h,
    )
    assert pack_r.status_code == 201
    pack_id = pack_r.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/skills",
        json={"skill_id": sid},
        headers=h,
    )
    rel1 = await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/releases",
        json={"version": "1.0.0"},
        headers=h,
    )
    assert rel1.status_code == 201

    # Install in consumer org
    inst_r = await c.post(
        f"/api/v1/orgs/{oid_con}/installations",
        json={"pack_id": pack_id},
        headers=h,
    )
    assert inst_r.status_code == 201
    install_id = inst_r.json()["data"]["id"]

    # Find the installed skill in consumer org (by origin_pack_id)
    from sqlalchemy import select as _sel

    from app.core.database import AsyncSessionLocal
    from app.models.skill import Skill

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            _sel(Skill).where(
                Skill.org_id == oid_con,
                Skill.origin_pack_id == pack_id,
            )
        )
        installed_skill = result.scalar_one()
        installed_skill_id = installed_skill.id

    # Edit the installed skill via PUT to trigger locally_modified=True
    edit_r = await c.put(
        f"/api/v1/orgs/{oid_con}/skills/{installed_skill_id}",
        json={"description": "MY LOCAL EDIT"},
        headers=h,
    )
    assert edit_r.status_code == 200

    # Verify locally_modified is set
    from sqlalchemy import text

    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text("SELECT locally_modified FROM skills WHERE id = :id"),
            {"id": installed_skill_id},
        )
        assert row.scalar_one() is True

    # Publish v1.1.0 with the SAME skill but different description
    # First update the source skill's description to differ from v1.0.0
    await c.put(
        f"/api/v1/orgs/{oid_pub}/skills/{sid}",
        json={"description": "UPSTREAM CHANGE"},
        headers=h,
    )
    rel2 = await c.post(
        f"/api/v1/orgs/{oid_pub}/packs/{pack_id}/releases",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert rel2.status_code == 201

    # Upgrade
    upg = await c.post(
        f"/api/v1/orgs/{oid_con}/installations/{install_id}/upgrade",
        json={"version": "1.1.0"},
        headers=h,
    )
    assert upg.status_code == 200
    assert upg.json()["data"]["installed_version"] == "1.1.0"

    # Verify the locally modified skill was NOT overwritten
    async with AsyncSessionLocal() as session:
        row = await session.execute(
            text("SELECT description FROM skills WHERE id = :id"),
            {"id": installed_skill_id},
        )
        desc = row.scalar_one()
        assert desc == "MY LOCAL EDIT", f"Expected 'MY LOCAL EDIT' but got '{desc}'"


@pytest.mark.asyncio
async def test_review_forbidden_for_owner_org_members(c):
    """R62: pack ownership is org-level; blocking self-review only on
    created_by let any OTHER member of the owning org rate the pack.
    Every active owner-org member must be blocked."""
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    pid = await _published_public_pack(c, h_owner, oid)

    # A second member of the SAME org
    h_member, member = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": member["id"], "role": "student"},
        headers=h_owner,
    )
    r = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 5}, headers=h_member
    )
    assert r.status_code == 422, r.text[:200]
    assert r.json()["error"]["code"] == "SELF_REVIEW_FORBIDDEN"

    # An outsider can still review
    h_out, _ = await _auth(c)
    r2 = await c.post(
        f"/api/v1/registry/packs/{pid}/reviews", json={"rating": 4}, headers=h_out
    )
    assert r2.status_code == 201, r2.text[:200]
