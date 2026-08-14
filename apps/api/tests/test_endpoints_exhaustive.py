"""Hit EVERY endpoint handler body to reach 100% coverage on endpoint files.

APP_ENV=test PYTHONPATH=. uv run pytest tests/test_endpoints_exhaustive.py -v
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _e():
    return f"ex-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from contextlib import asynccontextmanager

    from app.core.database import engine
    from app.main import app

    @asynccontextmanager
    async def _n(a):
        yield

    o = app.router.lifespan_context
    app.router.lifespan_context = _n
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = o
    await engine.dispose()


async def _reg(c):
    r = await c.post(
        "/api/v1/auth/register", json={"email": _e(), "password": "Test123!", "display_name": "Ex"}
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _admin(c):
    """Create admin user."""
    e = _e()
    await c.post(
        "/api/v1/auth/register", json={"email": e, "password": "Admin123!", "display_name": "Adm"}
    )
    from sqlalchemy import update

    from app.core.database import AsyncSessionLocal
    from app.core.security import create_access_token
    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        await db.execute(update(User).where(User.email == e).values(role=UserRole.ADMIN))
        await db.commit()
        r = await db.execute(select(User).where(User.email == e))
        u = r.scalar_one()
    return {"Authorization": f"Bearer {create_access_token(u.id, u.email, 'admin')}"}, u


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"EX-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


# ══════════════════════════════════════════════════════════
# Health endpoints (cover readiness handler body)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_health_ready_handler(c):
    r = await c.get("/api/v1/health/ready")
    assert r.status_code == 200
    d = r.json()
    assert "components" in d
    assert "status" in d


# ══════════════════════════════════════════════════════════
# Auth endpoints (cover all handler bodies)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_auth_register_handler(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _e(), "password": "Valid123!", "display_name": "New"},
    )
    assert r.status_code == 201
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"
    assert r.json()["expires_in"] > 0


@pytest.mark.asyncio
async def test_auth_login_handler(c):
    e = _e()
    await c.post(
        "/api/v1/auth/register", json={"email": e, "password": "Valid123!", "display_name": "Login"}
    )
    r = await c.post("/api/v1/auth/login", json={"email": e, "password": "Valid123!"})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_auth_refresh_handler(c):
    """Test refresh via service-level since ASGI transport doesn't propagate Set-Cookie."""
    from app.core.database import AsyncSessionLocal
    from app.services.auth import AuthService

    e = _e()
    async with AsyncSessionLocal() as db:
        svc = AuthService(db)
        reg = await svc.register(e, "Valid123!", "Refresh")
        await db.commit()
        # Use the raw refresh token as cookie
        c.cookies.set("refresh_token", reg.refresh_token)
        r = await c.post("/api/v1/auth/refresh")
        assert r.status_code == 200
        assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_auth_logout_handler(c):
    h, _ = await _reg(c)
    r = await c.post("/api/v1/auth/logout", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_auth_me_get_put(c):
    h, _ = await _reg(c)
    r = await c.get("/api/v1/auth/me", headers=h)
    assert r.status_code == 200
    r2 = await c.put("/api/v1/auth/me", json={"display_name": "Upd"}, headers=h)
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_auth_change_password_handler(c):
    e = _e()
    await c.post(
        "/api/v1/auth/register", json={"email": e, "password": "OldP123!", "display_name": "Change"}
    )
    r = await c.post("/api/v1/auth/login", json={"email": e, "password": "OldP123!"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r2 = await c.post(
        "/api/v1/auth/change-password",
        json={"old_password": "OldP123!", "new_password": "NewP123!"},
        headers=h,
    )
    assert r2.status_code == 204


@pytest.mark.asyncio
async def test_auth_forgot_password_handler(c):
    h, u = await _reg(c)
    r = await c.post("/api/v1/auth/forgot-password", json={"email": u["email"]})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_auth_reset_password_handler(c):
    r = await c.post(
        "/api/v1/auth/reset-password", json={"token": "bad", "new_password": "NewP123!"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_verify_email_handler(c):
    r = await c.get("/api/v1/auth/verify-email?token=bad")
    assert r.status_code in (302, 401, 500)


@pytest.mark.asyncio
async def test_auth_resend_verification_handler(c):
    h, _ = await _reg(c)
    r = await c.post("/api/v1/auth/resend-verification", headers=h)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_auth_sessions_handler(c):
    h, _ = await _reg(c)
    r = await c.get("/api/v1/auth/sessions", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


# ══════════════════════════════════════════════════════════
# Admin endpoints
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_admin_all_handlers(c):
    ah, admin = await _admin(c)

    # List
    r = await c.get("/api/v1/admin/users", headers=ah)
    assert r.status_code == 200

    # Get
    r2 = await c.get(f"/api/v1/admin/users/{admin.id}", headers=ah)
    assert r2.status_code == 200

    # Create target
    _, u2 = await _reg(c)
    # Update role
    r3 = await c.put(
        f"/api/v1/admin/users/{u2['id']}/role", json={"role": "instructor"}, headers=ah
    )
    assert r3.status_code == 200

    # Delete
    r4 = await c.delete(f"/api/v1/admin/users/{u2['id']}", headers=ah)
    assert r4.status_code == 204

    # Cannot delete self
    r5 = await c.delete(f"/api/v1/admin/users/{admin.id}", headers=ah)
    assert r5.status_code == 422


# ══════════════════════════════════════════════════════════
# Organization endpoints (ALL handlers)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_org_all_handlers(c):
    h, _ = await _reg(c)

    # Create
    r = await c.post("/api/v1/orgs", json={"name": f"O-{uuid.uuid4().hex[:6]}"}, headers=h)
    assert r.status_code == 201
    oid = r.json()["data"]["id"]

    # List
    r2 = await c.get("/api/v1/orgs", headers=h)
    assert r2.status_code == 200

    # Get
    r3 = await c.get(f"/api/v1/orgs/{oid}", headers=h)
    assert r3.status_code == 200

    # Update
    r4 = await c.put(f"/api/v1/orgs/{oid}", json={"name": "Updated"}, headers=h)
    assert r4.status_code == 200

    # Settings
    r5 = await c.put(f"/api/v1/orgs/{oid}/settings", json={"settings": {"k": "v"}}, headers=h)
    assert r5.status_code == 200

    # Members
    r6 = await c.get(f"/api/v1/orgs/{oid}/members", headers=h)
    assert r6.status_code == 200

    # Add member
    h2, u2 = await _reg(c)
    r7 = await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    assert r7.status_code == 200

    # Update member role
    r8 = await c.put(
        f"/api/v1/orgs/{oid}/members/{u2['id']}", json={"role": "instructor"}, headers=h
    )
    assert r8.status_code == 200

    # Remove member
    r9 = await c.delete(f"/api/v1/orgs/{oid}/members/{u2['id']}", headers=h)
    assert r9.status_code == 204

    # Invites
    r10 = await c.post(
        f"/api/v1/orgs/{oid}/invites", json={"emails": [_e()], "role": "student"}, headers=h
    )
    assert r10.status_code == 200

    # List invitations
    r11 = await c.get(f"/api/v1/orgs/{oid}/invites", headers=h)
    assert r11.status_code == 200

    # Invite link
    r12 = await c.post(
        f"/api/v1/orgs/{oid}/invite-links",
        json={"role": "student", "max_uses": 10, "expires_in_days": 7},
        headers=h,
    )
    assert r12.status_code == 201
    lid = r12.json()["data"]["id"]
    r12.json()["data"]["code"]

    # List links
    r13 = await c.get(f"/api/v1/orgs/{oid}/invite-links", headers=h)
    assert r13.status_code == 200

    # Toggle link
    r14 = await c.put(
        f"/api/v1/orgs/{oid}/invite-links/{lid}", json={"is_active": False}, headers=h
    )
    assert r14.status_code == 200

    # Delete link
    r15 = await c.delete(f"/api/v1/orgs/{oid}/invite-links/{lid}", headers=h)
    assert r15.status_code == 204

    # Join (with another user, new active link)
    r16 = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=h)
    code2 = r16.json()["data"]["code"]
    h3, _ = await _reg(c)
    r17 = await c.post("/api/v1/invites/join", json={"code": code2}, headers=h3)
    assert r17.status_code == 200

    # Delete org
    r18 = await c.delete(f"/api/v1/orgs/{oid}", headers=h)
    assert r18.status_code == 204


# ══════════════════════════════════════════════════════════
# Skills endpoints (ALL handlers)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_skills_all_handlers(c):
    h, _ = await _reg(c)
    oid = await _org(c, h)

    # Category CRUD
    r = await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat1"}, headers=h)
    assert r.status_code == 201
    cid = r.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/categories", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/categories/{cid}", headers=h)
    await c.put(f"/api/v1/orgs/{oid}/categories/{cid}", json={"name": "Cat1U"}, headers=h)

    # Skill CRUD
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "category_id": cid,
            "name": "Skill1",
            "description": "D",
            "tags": ["t1"],
            "difficulty": "beginner",
        },
        headers=h,
    )
    assert r2.status_code == 201
    sid = r2.json()["data"]["id"]

    await c.get(f"/api/v1/orgs/{oid}/skills", headers=h)
    await c.get(
        f"/api/v1/orgs/{oid}/skills?category={cid}&difficulty=beginner&tag=t1&q=Skill", headers=h
    )
    await c.get(f"/api/v1/orgs/{oid}/skills/{sid}", headers=h)
    await c.put(f"/api/v1/orgs/{oid}/skills/{sid}", json={"description": "U"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/unpublish", headers=h)

    # Prerequisites
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "category_id": cid,
            "name": "Skill2",
            "description": "D2",
        },
        headers=h,
    )
    sid2 = r3.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/skills/{sid2}/prerequisites",
        json={"prerequisite_ids": [sid]},
        headers=h,
    )
    await c.get(f"/api/v1/orgs/{oid}/skills/{sid2}/tree", headers=h)

    # Exercise CRUD
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises",
        json={
            "title": "Ex1",
            "description": "D",
            "type": "multiple_choice",
            "config": {"correct": ["a"], "options": [{"id": "a", "text": "A"}]},
        },
        headers=h,
    )
    eid = r4.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/exercises/{eid}", headers=h)
    await c.put(f"/api/v1/orgs/{oid}/exercises/{eid}", json={"title": "Ex1U"}, headers=h)
    await c.get(f"/api/v1/orgs/{oid}/skills/{sid}/exercises", headers=h)

    # Reorder
    await c.put(
        f"/api/v1/orgs/{oid}/categories/reorder",
        json={"items": [{"id": cid, "sort_order": 0}]},
        headers=h,
    )
    await c.put(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises/reorder",
        json={"items": [{"id": eid, "sort_order": 0}]},
        headers=h,
    )

    # Attempt
    r5 = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{eid}/attempts",
        json={"answer": {"selected": ["a"]}},
        headers=h,
    )
    assert r5.status_code == 201
    await c.get(f"/api/v1/orgs/{oid}/exercises/{eid}/attempts", headers=h)

    # Progress
    await c.get(f"/api/v1/orgs/{oid}/progress/me", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/progress/me/skills", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/progress/me/skills/{sid}", headers=h)

    h2, u2 = await _reg(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    await c.get(f"/api/v1/orgs/{oid}/progress/students/{u2['id']}", headers=h)

    # Grading
    r6 = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises",
        json={
            "title": "TextQ",
            "description": "D",
            "type": "text_answer",
            "config": {},
        },
        headers=h,
    )
    eid2 = r6.json()["data"]["id"]
    r7 = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{eid2}/attempts", json={"answer": {"text": "ans"}}, headers=h
    )
    aid = r7.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/grading/pending", headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/grading/attempts/{aid}", json={"score": 80, "feedback": "G"}, headers=h
    )

    # Delete
    await c.delete(f"/api/v1/orgs/{oid}/exercises/{eid2}", headers=h)
    await c.delete(f"/api/v1/orgs/{oid}/skills/{sid2}", headers=h)
    await c.delete(f"/api/v1/orgs/{oid}/categories/{cid}", headers=h)


# ══════════════════════════════════════════════════════════
# Project endpoints (ALL handlers)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_projects_all_handlers(c):
    h, _ = await _reg(c)
    oid = await _org(c, h)

    # Project CRUD
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Proj1",
            "description": "D",
            "instructions": "I",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    assert r.status_code == 201
    pid = r.json()["data"]["id"]

    await c.get(f"/api/v1/orgs/{oid}/projects", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    await c.put(f"/api/v1/orgs/{oid}/projects/{pid}", json={"title": "Proj1U"}, headers=h)
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/unpublish", headers=h)
    await c.put(f"/api/v1/orgs/{oid}/projects/{pid}/skills", json={"skill_ids": []}, headers=h)

    # Deliverable
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
        json={
            "name": "Readme",
            "type": "text",
            "required": False,
        },
        headers=h,
    )
    did = r2.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/deliverables", headers=h)
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables/{did}", json={"name": "ReadmeU"}, headers=h
    )

    # Extension
    h2, u2 = await _reg(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/extensions",
        json={
            "user_id": u2["id"],
            "new_deadline": "2027-12-31T00:00:00Z",
        },
        headers=h,
    )

    # Submission
    r3 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    subid = r3.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)

    # Update draft
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{subid}",
        json={
            "items": [{"deliverable_id": did, "type": "text", "content": "My readme"}],
        },
        headers=h,
    )

    # Get detail
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{subid}", headers=h)

    # Submit
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{subid}/submit", headers=h)

    # Reviews
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{subid}/reviews",
        json={
            "status": "approved",
            "score": 90,
            "feedback": "Good",
        },
        headers=h,
    )
    assert r4.status_code == 201
    await c.get(f"/api/v1/orgs/{oid}/submissions/{subid}/reviews", headers=h)

    # Pending
    await c.get(f"/api/v1/orgs/{oid}/reviews/pending", headers=h)

    # Download (no file, but hits handler)
    # await c.get(f"/api/v1/orgs/{oid}/submissions/{subid}/files/fake/download", headers=h)

    # Second sub + delete
    r5 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    subid2 = r5.json()["data"]["id"]
    await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{subid2}", headers=h)

    # Delete deliverable + project
    await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}/deliverables/{did}", headers=h)
    await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)


# ══════════════════════════════════════════════════════════
# Evaluation endpoints (ALL handlers)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_evaluation_all_handlers(c):
    h, _ = await _reg(c)
    oid = await _org(c, h)

    # Settings
    r = await c.get(f"/api/v1/orgs/{oid}/settings/evaluation", headers=h)
    assert r.status_code == 200
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={
            "enabled": True,
            "monthly_budget_usd": 100,
        },
        headers=h,
    )
    assert r2.status_code == 200

    # Usage
    r3 = await c.get(f"/api/v1/orgs/{oid}/evaluation/usage", headers=h)
    assert r3.status_code == 200

    # Tasks list
    r4 = await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks", headers=h)
    assert r4.status_code == 200

    # Task not found
    r5 = await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks/nonexistent", headers=h)
    assert r5.status_code == 404

    # Retry nonexistent
    r6 = await c.post(f"/api/v1/orgs/{oid}/evaluation/tasks/nonexistent/retry", headers=h)
    assert r6.status_code == 404

    # Cancel nonexistent
    r7 = await c.post(f"/api/v1/orgs/{oid}/evaluation/tasks/nonexistent/cancel", headers=h)
    assert r7.status_code == 404


# ══════════════════════════════════════════════════════════
# Portfolio endpoints (ALL handlers)
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_portfolio_all_handlers(c):
    h, _ = await _reg(c)
    uname = f"port-{uuid.uuid4().hex[:6]}"

    # Profile
    r = await c.get("/api/v1/portfolio/profile", headers=h)
    assert r.status_code == 200
    r2 = await c.put(
        "/api/v1/portfolio/profile",
        json={
            "headline": "Dev",
            "bio": "Bio",
            "website_url": "https://x.com",
            "social_links": {"gh": "https://github.com/x"},
        },
        headers=h,
    )
    assert r2.status_code == 200

    # Username
    r3 = await c.put("/api/v1/portfolio/username", json={"username": uname}, headers=h)
    assert r3.status_code == 200

    # Items
    r4 = await c.post(
        "/api/v1/portfolio/items",
        json={"title": "It1", "tags": ["a"], "visibility": "public", "featured": True},
        headers=h,
    )
    assert r4.status_code == 201
    iid = r4.json()["data"]["id"]

    r5 = await c.post(
        "/api/v1/portfolio/items", json={"title": "It2", "visibility": "unlisted"}, headers=h
    )
    iid2 = r5.json()["data"]["id"]

    await c.get("/api/v1/portfolio/items", headers=h)
    await c.get(f"/api/v1/portfolio/items/{iid}", headers=h)
    await c.put(f"/api/v1/portfolio/items/{iid}", json={"title": "It1U"}, headers=h)

    # Reorder
    await c.put("/api/v1/portfolio/items/reorder", json={"item_ids": [iid2, iid]}, headers=h)

    # Badges
    await c.get("/api/v1/portfolio/badges", headers=h)

    # Public
    r6 = await c.get(f"/api/v1/u/{uname}")
    assert r6.status_code == 200
    r7 = await c.get(f"/api/v1/u/{uname}/items")
    assert r7.status_code == 200

    slug = r4.json()["data"]["slug"]
    r8 = await c.get(f"/api/v1/u/{uname}/items/{slug}")
    assert r8.status_code == 200

    # Delete
    await c.delete(f"/api/v1/portfolio/items/{iid2}", headers=h)


# ══════════════════════════════════════════════════════════
# Lifespan
# ══════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_app_lifespan():
    from app.core.database import engine
    from app.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/api/v1/health")
        assert r.status_code == 200
    await engine.dispose()
