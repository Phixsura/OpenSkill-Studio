"""Tests for error paths and edge cases to maximize coverage."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"err-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from contextlib import asynccontextmanager

    from app.core.database import engine
    from app.main import app

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={
            "email": _email(),
            "password": "TestPass123!",
            "display_name": "Err",
        },
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"E-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


# ── Auth error paths ──


@pytest.mark.asyncio
async def test_login_nonexistent(c):
    r = await c.post("/api/v1/auth/login", json={"email": "nobody@x.com", "password": "X123456!"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_change_password_wrong_old(c):
    h, _ = await _auth(c)
    r = await c.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "Wrong123!",
            "new_password": "New123456!",
        },
        headers=h,
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_refresh_no_cookie(c):
    r = await c.post("/api/v1/auth/refresh")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_bad_token(c):
    r = await c.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "bad-token",
            "new_password": "NewPass123!",
        },
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_verify_email_bad_token(c):
    r = await c.get("/api/v1/auth/verify-email?token=bad-token")
    # Should return error (401 or redirect)
    assert r.status_code in (302, 401, 500)


# ── Org error paths ──


@pytest.mark.asyncio
async def test_org_not_found(c):
    h, _ = await _auth(c)
    r = await c.get("/api/v1/orgs/nonexistent", headers=h)
    assert r.status_code == 404  # Org not found


@pytest.mark.asyncio
async def test_org_duplicate_slug(c):
    h, _ = await _auth(c)
    slug = f"dup-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/orgs", json={"name": "Org1", "slug": slug}, headers=h)
    r = await c.post("/api/v1/orgs", json={"name": "Org2", "slug": slug}, headers=h)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_org_member_role_update(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Add member
    h2, u2 = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )

    # Update role
    r = await c.put(
        f"/api/v1/orgs/{oid}/members/{u2['id']}", json={"role": "instructor"}, headers=h
    )
    assert r.status_code == 200

    # Remove member
    r2 = await c.delete(f"/api/v1/orgs/{oid}/members/{u2['id']}", headers=h)
    assert r2.status_code == 204


@pytest.mark.asyncio
async def test_invite_link_join_active(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create active link
    r = await c.post(
        f"/api/v1/orgs/{oid}/invite-links", json={"role": "student", "max_uses": 5}, headers=h
    )
    code = r.json()["data"]["code"]

    # Join with new user
    h2, _ = await _auth(c)
    r2 = await c.post("/api/v1/invites/join", json={"code": code}, headers=h2)
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_invite_link_not_found(c):
    h, _ = await _auth(c)
    r = await c.post("/api/v1/invites/join", json={"code": "nonexistent"}, headers=h)
    assert r.status_code == 422


# ── Skill error paths ──


@pytest.mark.asyncio
async def test_skill_not_found(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.get(f"/api/v1/orgs/{oid}/skills/nonexistent", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_exercise_wrong_answer(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Test"}, headers=h)
    cid = r.json()["data"]["id"]

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "category_id": cid,
            "name": "Skill",
            "description": "D",
        },
        headers=h,
    )
    sid = r2.json()["data"]["id"]

    r3 = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises",
        json={
            "title": "Quiz MCQ",
            "description": "D",
            "type": "multiple_choice",
            "config": {
                "correct": ["b", "c"],
                "options": [
                    {"id": "a", "text": "W"},
                    {"id": "b", "text": "R"},
                    {"id": "c", "text": "R2"},
                ],
                "multiple": True,
            },
        },
        headers=h,
    )
    assert r3.status_code == 201, f"Exercise create failed: {r3.text}"
    eid = r3.json()["data"]["id"]

    # Wrong answer
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{eid}/attempts",
        json={
            "answer": {"selected": ["a"]},
        },
        headers=h,
    )
    assert r4.json()["data"]["is_correct"] is False
    assert r4.json()["data"]["score"] == 0


@pytest.mark.asyncio
async def test_skill_delete_and_list(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Del"}, headers=h)
    cid = r.json()["data"]["id"]

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "category_id": cid,
            "name": "ToDelete",
            "description": "D",
        },
        headers=h,
    )
    sid = r2.json()["data"]["id"]
    await c.delete(f"/api/v1/orgs/{oid}/skills/{sid}", headers=h)

    # List should still work
    r3 = await c.get(f"/api/v1/orgs/{oid}/skills", headers=h)
    assert r3.status_code == 200


# ── Project error paths ──


@pytest.mark.asyncio
async def test_project_not_found(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.get(f"/api/v1/orgs/{oid}/projects/nonexistent", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_submission_not_owner(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Project Test",
            "description": "D",
            "instructions": "I",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]

    r2 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    assert r2.status_code == 201, f"Submission create failed: {r2.text}"
    sub_id = r2.json()["data"]["id"]

    # Try to submit with different user
    h2, u2 = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    r3 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}/submit", headers=h2)
    assert r3.status_code == 403


@pytest.mark.asyncio
async def test_review_revision_requested(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Rev",
            "description": "D",
            "instructions": "I",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]

    r2 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    sub_id = r2.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}/submit", headers=h)

    # Review: request revision
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sub_id}/reviews",
        json={
            "status": "revision_requested",
            "feedback": "Needs work",
        },
        headers=h,
    )
    assert r3.status_code == 201

    # Check status
    r4 = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}", headers=h)
    assert r4.json()["data"]["status"] == "revision_requested"


@pytest.mark.asyncio
async def test_review_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Rej",
            "description": "D",
            "instructions": "I",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]

    r2 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    sub_id = r2.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}/submit", headers=h)

    r3 = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sub_id}/reviews",
        json={
            "status": "rejected",
            "score": 20,
            "feedback": "Poor",
        },
        headers=h,
    )
    assert r3.status_code == 201


# ── Portfolio error paths ──


@pytest.mark.asyncio
async def test_portfolio_item_not_found(c):
    h, _ = await _auth(c)
    r = await c.get("/api/v1/portfolio/items/nonexistent", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_portfolio_delete_not_owner(c):
    h, _ = await _auth(c)
    r = await c.post("/api/v1/portfolio/items", json={"title": "Mine"}, headers=h)
    item_id = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    r2 = await c.delete(f"/api/v1/portfolio/items/{item_id}", headers=h2)
    assert r2.status_code in (403, 404)


@pytest.mark.asyncio
async def test_public_profile_not_found(c):
    r = await c.get("/api/v1/u/nonexistent-user-xyz")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_portfolio_username_taken(c):
    h1, _ = await _auth(c)
    name = f"taken-{uuid.uuid4().hex[:6]}"
    await c.put("/api/v1/portfolio/username", json={"username": name}, headers=h1)

    h2, _ = await _auth(c)
    # Need to create profile first
    await c.get("/api/v1/portfolio/profile", headers=h2)
    r = await c.put("/api/v1/portfolio/username", json={"username": name}, headers=h2)
    assert r.status_code == 409


# ── Evaluation error paths ──


@pytest.mark.asyncio
async def test_eval_task_not_found(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks/nonexistent", headers=h)
    assert r.status_code == 404


# ── Lifespan (cover main.py) ──


@pytest.mark.asyncio
async def test_lifespan_runs():
    """Test that the app lifespan works with real infra."""
    from httpx import ASGITransport, AsyncClient

    from app.core.database import engine
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/health")
        assert r.status_code == 200
    await engine.dispose()
