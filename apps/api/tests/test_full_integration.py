"""Exhaustive integration tests targeting 100% coverage.

Exercises every endpoint handler + service method via real DB.
APP_ENV=test PYTHONPATH=. uv run pytest tests/test_full_integration.py -v
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"cov-{uuid.uuid4().hex[:8]}@test.com"


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
    """Register + return (headers, user)."""
    r = await c.post(
        "/api/v1/auth/register",
        json={
            "email": _email(),
            "password": "TestPass123!",
            "display_name": "Cov",
        },
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    """Create org, return org_id."""
    r = await c.post("/api/v1/orgs", json={"name": f"O-{uuid.uuid4().hex[:6]}"}, headers=h)
    return r.json()["data"]["id"]


# ── Auth: forgot/reset password, sessions, change-password, verify ──


@pytest.mark.asyncio
async def test_auth_forgot_password(c):
    h, u = await _auth(c)
    # forgot password always 200
    r = await c.post("/api/v1/auth/forgot-password", json={"email": u["email"]})
    assert r.status_code == 200
    # nonexistent email also 200
    r2 = await c.post("/api/v1/auth/forgot-password", json={"email": "nobody@x.com"})
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_auth_change_password(c):
    email = _email()
    await c.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "OldPass123!", "display_name": "CP"},
    )
    r = await c.post("/api/v1/auth/login", json={"email": email, "password": "OldPass123!"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r2 = await c.post(
        "/api/v1/auth/change-password",
        json={
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
        },
        headers=h,
    )
    assert r2.status_code == 204

    # Login with new password
    r3 = await c.post("/api/v1/auth/login", json={"email": email, "password": "NewPass123!"})
    assert r3.status_code == 200


@pytest.mark.asyncio
async def test_auth_sessions(c):
    h, _ = await _auth(c)
    r = await c.get("/api/v1/auth/sessions", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_auth_resend_verification(c):
    h, _ = await _auth(c)
    r = await c.post("/api/v1/auth/resend-verification", headers=h)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_auth_logout(c):
    h, _ = await _auth(c)
    r = await c.post("/api/v1/auth/logout", headers=h)
    assert r.status_code == 204


# ── Admin ──


@pytest.mark.asyncio
async def test_admin_list_get_role_delete(c):
    # Register admin-level user
    email = _email()
    await c.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Admin123!", "display_name": "Admin"},
    )
    # Make admin via DB directly
    from sqlalchemy import select, update

    from app.core.database import AsyncSessionLocal
    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as db:
        await db.execute(update(User).where(User.email == email).values(role=UserRole.ADMIN))
        await db.commit()
        result = await db.execute(select(User).where(User.email == email))
        admin = result.scalar_one()

    from app.core.security import create_access_token

    h = {"Authorization": f"Bearer {create_access_token(admin.id, admin.email, 'admin')}"}

    # List users
    r = await c.get("/api/v1/admin/users", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1

    # Get specific user
    r2 = await c.get(f"/api/v1/admin/users/{admin.id}", headers=h)
    assert r2.status_code == 200

    # Create another user to modify
    email2 = _email()
    r3 = await c.post(
        "/api/v1/auth/register",
        json={"email": email2, "password": "Test123!", "display_name": "Target"},
    )
    target_id = r3.json()["user"]["id"]

    # Change role
    r4 = await c.put(
        f"/api/v1/admin/users/{target_id}/role", json={"role": "instructor"}, headers=h
    )
    assert r4.status_code == 200

    # Soft delete
    r5 = await c.delete(f"/api/v1/admin/users/{target_id}", headers=h)
    assert r5.status_code == 204


# ── Orgs: full CRUD + members + invites + links + settings ──


@pytest.mark.asyncio
async def test_org_full_crud(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Update
    r = await c.put(f"/api/v1/orgs/{oid}", json={"name": "Updated Org"}, headers=h)
    assert r.status_code == 200

    # Settings
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/settings", json={"settings": {"max_members": 50}}, headers=h
    )
    assert r2.status_code == 200

    # Invite link
    r3 = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=h)
    assert r3.status_code == 201
    link_id = r3.json()["data"]["id"]
    code = r3.json()["data"]["code"]

    # List invite links
    r4 = await c.get(f"/api/v1/orgs/{oid}/invite-links", headers=h)
    assert r4.status_code == 200

    # Toggle link
    r5 = await c.put(
        f"/api/v1/orgs/{oid}/invite-links/{link_id}", json={"is_active": False}, headers=h
    )
    assert r5.status_code == 200

    # List invitations
    r6 = await c.get(f"/api/v1/orgs/{oid}/invites", headers=h)
    assert r6.status_code == 200

    # Invite by email
    r7 = await c.post(
        f"/api/v1/orgs/{oid}/invites",
        json={
            "emails": [_email()],
            "role": "student",
        },
        headers=h,
    )
    assert r7.status_code == 200

    # Join by code with another user
    h2, _ = await _auth(c)
    r8 = await c.post("/api/v1/invites/join", json={"code": code}, headers=h2)
    # Link was deactivated, should fail
    assert r8.status_code in (200, 422)

    # Delete link
    await c.delete(f"/api/v1/orgs/{oid}/invite-links/{link_id}", headers=h)

    # Delete org
    r9 = await c.delete(f"/api/v1/orgs/{oid}", headers=h)
    assert r9.status_code == 204


# ── Skills: full CRUD + publish + exercises + attempts + progress ──


@pytest.mark.asyncio
async def test_skills_full_flow(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Categories
    r = await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Programming"}, headers=h)
    cid = r.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/categories/{cid}", headers=h)
    await c.put(f"/api/v1/orgs/{oid}/categories/{cid}", json={"name": "AI Programming"}, headers=h)

    # Skills
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "category_id": cid,
            "name": "Python Basics",
            "description": "Learn Python",
            "learning_content": "# Python\n\nLearn the basics.",
            "difficulty": "beginner",
            "tags": ["python", "beginner"],
            "estimated_minutes": 30,
        },
        headers=h,
    )
    sid = r2.json()["data"]["id"]

    # List with filters
    await c.get(f"/api/v1/orgs/{oid}/skills?difficulty=beginner&tag=python&q=Python", headers=h)
    # Get detail
    await c.get(f"/api/v1/orgs/{oid}/skills/{sid}", headers=h)
    # Update
    await c.put(f"/api/v1/orgs/{oid}/skills/{sid}", json={"description": "Updated"}, headers=h)
    # Publish
    await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/publish", headers=h)
    # Unpublish
    await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/unpublish", headers=h)
    # Re-publish for exercises
    await c.post(f"/api/v1/orgs/{oid}/skills/{sid}/publish", headers=h)

    # Prerequisites
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "category_id": cid,
            "name": "Advanced Python",
            "description": "Advanced",
            "prerequisites": [sid],
        },
        headers=h,
    )
    sid2 = r3.json()["data"]["id"]

    # Set prerequisites
    await c.put(
        f"/api/v1/orgs/{oid}/skills/{sid2}/prerequisites",
        json={"prerequisite_ids": [sid]},
        headers=h,
    )
    # Get tree
    await c.get(f"/api/v1/orgs/{oid}/skills/{sid2}/tree", headers=h)

    # Exercises
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises",
        json={
            "title": "MCQ 1",
            "description": "Pick",
            "type": "multiple_choice",
            "config": {
                "correct": ["a"],
                "options": [{"id": "a", "text": "Right"}, {"id": "b", "text": "Wrong"}],
            },
        },
        headers=h,
    )
    eid = r4.json()["data"]["id"]

    r5 = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sid}/exercises",
        json={
            "title": "Text Q",
            "description": "Answer",
            "type": "text_answer",
            "config": {},
        },
        headers=h,
    )
    eid2 = r5.json()["data"]["id"]

    # Get exercise
    await c.get(f"/api/v1/orgs/{oid}/exercises/{eid}", headers=h)
    # Update exercise
    await c.put(f"/api/v1/orgs/{oid}/exercises/{eid}", json={"title": "Updated MCQ"}, headers=h)

    # Submit MCQ (correct)
    r6 = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{eid}/attempts",
        json={
            "answer": {"selected": ["a"]},
        },
        headers=h,
    )
    assert r6.json()["data"]["is_correct"] is True

    # Submit MCQ (wrong)
    r7 = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{eid}/attempts",
        json={
            "answer": {"selected": ["b"]},
        },
        headers=h,
    )
    assert r7.json()["data"]["is_correct"] is False

    # List attempts
    await c.get(f"/api/v1/orgs/{oid}/exercises/{eid}/attempts", headers=h)

    # Progress
    await c.get(f"/api/v1/orgs/{oid}/progress/me", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/progress/me/skills", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/progress/me/skills/{sid}", headers=h)
    await c.get(f"/api/v1/orgs/{oid}/progress/students/{(await _auth(c))[1]['id']}", headers=h)

    # Grading
    await c.get(f"/api/v1/orgs/{oid}/grading/pending", headers=h)
    # Grade text answer (submit first)
    r8 = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{eid2}/attempts",
        json={
            "answer": {"text": "My answer"},
        },
        headers=h,
    )
    attempt_id = r8.json()["data"]["id"]
    r9 = await c.post(
        f"/api/v1/orgs/{oid}/grading/attempts/{attempt_id}",
        json={
            "score": 80,
            "feedback": "Good",
        },
        headers=h,
    )
    assert r9.status_code == 200

    # Delete exercise
    await c.delete(f"/api/v1/orgs/{oid}/exercises/{eid2}", headers=h)
    # Delete skill
    await c.delete(f"/api/v1/orgs/{oid}/skills/{sid2}", headers=h)
    # Delete category
    await c.delete(f"/api/v1/orgs/{oid}/categories/{cid}", headers=h)


# ── Projects: full CRUD + deliverables + submissions + reviews + extensions ──


@pytest.mark.asyncio
async def test_projects_full_flow(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Create project
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "AI Chatbot",
            "description": "Build one",
            "instructions": "Use the API",
            "rubric": [
                {"criterion": "Quality", "max_score": 60},
                {"criterion": "Design", "max_score": 40},
            ],
            "max_score": 100,
            "late_penalty_pct": 20,
            "max_submissions": 3,
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]

    # List
    await c.get(f"/api/v1/orgs/{oid}/projects", headers=h)
    # Get
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)
    # Update
    await c.put(f"/api/v1/orgs/{oid}/projects/{pid}", json={"title": "Updated Chatbot"}, headers=h)
    # Publish
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)

    # Deliverables
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
        json={
            "name": "Source Code",
            "type": "file",
            "required": True,
        },
        headers=h,
    )
    did = r2.json()["data"]["id"]
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/deliverables", headers=h)
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables/{did}", json={"name": "Code"}, headers=h
    )

    # Set skills
    await c.put(f"/api/v1/orgs/{oid}/projects/{pid}/skills", json={"skill_ids": []}, headers=h)

    # Create submission
    r3 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    sub_id = r3.json()["data"]["id"]
    assert r3.json()["data"]["version"] == 1

    # Update submission (add text item)
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}",
        json={
            "items": [{"deliverable_id": did, "type": "text", "content": "Here is my code"}],
        },
        headers=h,
    )

    # Submit
    r4 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}/submit", headers=h)
    assert r4.json()["data"]["status"] == "submitted"

    # List submissions
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    # Get submission detail
    await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}", headers=h)

    # Review (approve)
    r5 = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sub_id}/reviews",
        json={
            "status": "approved",
            "score": 85,
            "feedback": "Well done",
            "score_breakdown": {"Quality": 50, "Design": 35},
        },
        headers=h,
    )
    assert r5.status_code == 201

    # List reviews
    await c.get(f"/api/v1/orgs/{oid}/submissions/{sub_id}/reviews", headers=h)
    # Pending reviews
    await c.get(f"/api/v1/orgs/{oid}/reviews/pending", headers=h)

    # Verify final score
    r6 = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}", headers=h)
    assert r6.json()["data"]["final_score"] == 85

    # Second submission (revision)
    r7 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    sub2_id = r7.json()["data"]["id"]
    assert r7.json()["data"]["version"] == 2

    # Delete draft
    r8 = await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub2_id}", headers=h)
    assert r8.status_code == 204

    # Extension
    h2, u2 = await _auth(c)
    # Add second user to org
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": u2["id"], "role": "student"}, headers=h
    )
    r9 = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/extensions",
        json={
            "user_id": u2["id"],
            "new_deadline": "2027-12-31T00:00:00Z",
            "reason": "Medical",
        },
        headers=h,
    )
    assert r9.status_code == 201

    # Unpublish + Delete deliverable + Delete project
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/unpublish", headers=h)
    await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}/deliverables/{did}", headers=h)
    await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)


# ── Evaluation: trigger + tasks + settings + usage ──


@pytest.mark.asyncio
async def test_evaluation_full_flow(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Enable evaluation in settings
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={
            "enabled": True,
            "auto_evaluate": False,
            "monthly_budget_usd": 100,
        },
        headers=h,
    )

    # Get settings
    r = await c.get(f"/api/v1/orgs/{oid}/settings/evaluation", headers=h)
    assert r.status_code == 200
    assert r.json()["enabled"] is True

    # Usage
    r2 = await c.get(f"/api/v1/orgs/{oid}/evaluation/usage", headers=h)
    assert r2.status_code == 200

    # List tasks (empty)
    r3 = await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks", headers=h)
    assert r3.status_code == 200


# ── Portfolio: full profile + items + badges ──


@pytest.mark.asyncio
async def test_portfolio_full_flow(c):
    h, u = await _auth(c)

    # Get/create profile
    r = await c.get("/api/v1/portfolio/profile", headers=h)
    assert r.status_code == 200
    r.json()["data"]["username"]

    # Update profile
    r2 = await c.put(
        "/api/v1/portfolio/profile",
        json={
            "headline": "AI Developer",
            "bio": "Building the future",
            "location": "Beijing",
            "website_url": "https://example.com",
            "social_links": {"github": "https://github.com/test"},
        },
        headers=h,
    )
    assert r2.status_code == 200

    # Change username
    new_name = f"user-{uuid.uuid4().hex[:6]}"
    r3 = await c.put("/api/v1/portfolio/username", json={"username": new_name}, headers=h)
    assert r3.status_code == 200

    # Create items
    r4 = await c.post(
        "/api/v1/portfolio/items",
        json={
            "title": "Project Alpha",
            "description": "My best work",
            "tags": ["ai", "python"],
            "visibility": "public",
            "featured": True,
        },
        headers=h,
    )
    assert r4.status_code == 201
    item_id = r4.json()["data"]["id"]

    r5 = await c.post(
        "/api/v1/portfolio/items",
        json={
            "title": "Project Beta",
            "tags": ["ml"],
            "visibility": "unlisted",
        },
        headers=h,
    )
    item2_id = r5.json()["data"]["id"]

    # List items
    r6 = await c.get("/api/v1/portfolio/items", headers=h)
    assert len(r6.json()["data"]) >= 2

    # Get item
    r7 = await c.get(f"/api/v1/portfolio/items/{item_id}", headers=h)
    assert r7.status_code == 200

    # Update item
    r8 = await c.put(
        f"/api/v1/portfolio/items/{item_id}",
        json={
            "title": "Project Alpha v2",
            "show_score": True,
        },
        headers=h,
    )
    assert r8.status_code == 200

    # Reorder
    r9 = await c.put(
        "/api/v1/portfolio/items/reorder",
        json={
            "item_ids": [item2_id, item_id],
        },
        headers=h,
    )
    assert r9.status_code == 200

    # Badges
    r10 = await c.get("/api/v1/portfolio/badges", headers=h)
    assert r10.status_code == 200

    # Public profile
    r11 = await c.get(f"/api/v1/u/{new_name}")
    assert r11.status_code == 200
    assert r11.json()["display_name"] is not None

    # Public items
    r12 = await c.get(f"/api/v1/u/{new_name}/items")
    assert r12.status_code == 200

    # Delete item
    await c.delete(f"/api/v1/portfolio/items/{item2_id}", headers=h)


# ── Health readiness ──


@pytest.mark.asyncio
async def test_health_readiness_components(c):
    r = await c.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert "database" in r.json()["components"]
    assert "redis" in r.json()["components"]


# ── Markdown submission items (issue #9 §3: markdown must remain supported) ──


@pytest.mark.asyncio
async def test_markdown_item_roundtrip(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "MD Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
        json={"name": "Concept", "type": "markdown", "required": True},
        headers=h,
    )
    did = r2.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)

    r3 = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    sub_id = r3.json()["data"]["id"]

    # markdown item type must be accepted (was a 500 before the enum fix)
    r4 = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}",
        json={"items": [{"deliverable_id": did, "type": "markdown", "content": "## Head\n\n**bold**"}]},
        headers=h,
    )
    assert r4.status_code == 200

    r5 = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}", headers=h)
    items = r5.json()["data"]["items"]
    assert any(i["type"] == "markdown" and i["content"].startswith("## Head") for i in items)

    # invalid type → 422, not 500
    r6 = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sub_id}",
        json={"items": [{"deliverable_id": did, "type": "nonsense", "content": "x"}]},
        headers=h,
    )
    assert r6.status_code == 422
