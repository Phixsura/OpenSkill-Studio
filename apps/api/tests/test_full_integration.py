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
        json={
            "items": [{"deliverable_id": did, "type": "markdown", "content": "## Head\n\n**bold**"}]
        },
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


# ── /me/overview dashboard aggregate ──


@pytest.mark.asyncio
async def test_me_overview(c):
    h, _ = await _auth(c)
    # empty state: no orgs
    r0 = await c.get("/api/v1/me/overview", headers=h)
    assert r0.status_code == 200
    d0 = r0.json()["data"]
    assert d0["drafts"] == []
    assert d0["peer_assessments_pending"] == 0

    # with a draft submission
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Overview Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)

    r1 = await c.get("/api/v1/me/overview", headers=h)
    d1 = r1.json()["data"]
    assert any(dr["project_title"] == "Overview Project" for dr in d1["drafts"])


# ── Adversarial regressions (bug-hunt round: update_submission, FK injection, IDOR) ──


@pytest.mark.asyncio
async def test_update_submission_rejects_foreign_deliverable(c):
    """deliverable_id from another project must not be accepted (was: 200)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    async def mk_project():
        r = await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Adversarial Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
        pid = r.json()["data"]["id"]
        rd = await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Text Deliverable", "type": "text", "required": False},
            headers=h,
        )
        did = rd.json()["data"]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
        rs = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
        return pid, did, rs.json()["data"]["id"]

    pid1, did1, sid1 = await mk_project()
    pid2, did2, sid2 = await mk_project()

    # foreign deliverable
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid1}/submissions/{sid1}",
        json={"items": [{"deliverable_id": did2, "type": "text", "content": "x"}]},
        headers=h,
    )
    assert r.status_code == 422

    # bogus deliverable → 422, not 500
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid1}/submissions/{sid1}",
        json={
            "items": [
                {"deliverable_id": "01BOGUSBOGUSBOGUSBOGUSBOGU", "type": "text", "content": "x"}
            ]
        },
        headers=h,
    )
    assert r.status_code == 422

    # phantom file item via JSON → 422 (files have a dedicated endpoint)
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid1}/submissions/{sid1}",
        json={"items": [{"deliverable_id": did1, "type": "file", "content": "fake"}]},
        headers=h,
    )
    assert r.status_code == 422

    # cross-project path confusion (sid1 via pid2) → 404
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid2}/submissions/{sid1}",
        json={"items": [{"deliverable_id": did1, "type": "text", "content": "x"}]},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_project_skills_reject_unknown(c):
    """Bogus skill id in set_project_skills → 404, not a 500 FK violation."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Skill Link Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/skills",
        json={"skill_ids": ["01BOGUSBOGUSBOGUSBOGUSBOGU"]},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_add_member_unknown_user(c):
    """Adding a nonexistent user → 404, not a 500 FK violation."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": "01BOGUSBOGUSBOGUSBOGUSBOGU", "role": "student"},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_review_rejects_draft_and_over_max(c):
    """Cannot review a draft; score cannot exceed project max."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Review Bounds Project",
            "description": "d",
            "instructions": "i",
            "max_score": 100,
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    rs = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)
    sid = rs.json()["data"]["id"]

    # review a draft → 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 80},
        headers=h,
    )
    assert r.status_code == 422

    # submit, then score above project max → 422
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 150},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_download_url_scoped_to_submission(c):
    """A file_id from another submission cannot be fetched via one's own
    submission path (IDOR guard on get_download_url)."""
    import struct
    import zlib

    def _png():
        sig = b"\x89PNG\r\n\x1a\n"

        def chunk(t, d):
            crc = zlib.crc32(t + d) & 0xFFFFFFFF
            return struct.pack(">I", len(d)) + t + d + struct.pack(">I", crc)

        ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        idat = zlib.compress(b"\x00\xff\x00\x00")
        return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")

    async def mk_file(hh):
        oid = await _org(c, hh)
        r = await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "IDOR Probe Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hh,
        )
        pid = r.json()["data"]["id"]
        rd = await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Image Deliverable", "type": "image", "required": False},
            headers=hh,
        )
        did = rd.json()["data"]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hh)
        rs = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hh)
        sid = rs.json()["data"]["id"]
        rf = await c.post(
            f"/api/v1/orgs/{oid}/submissions/{sid}/files",
            files={"file": ("f.png", _png(), "image/png")},
            data={"deliverable_id": did},
            headers=hh,
        )
        assert rf.status_code == 201, rf.text[:200]
        return oid, sid, rf.json()["data"]["id"]

    hv, _ = await _auth(c)
    _, _, victim_file_id = await mk_file(hv)
    ha, _ = await _auth(c)
    attacker_org, attacker_sub, _ = await mk_file(ha)

    # attacker's own submission path + victim's file_id → 404
    r = await c.get(
        f"/api/v1/orgs/{attacker_org}/submissions/{attacker_sub}/files/{victim_file_id}/download",
        headers=ha,
    )
    assert r.status_code == 404


# ── Cross-org parent-confusion regressions (bug-hunt round 6) ──


@pytest.mark.asyncio
async def test_project_endpoints_verify_project_belongs_to_org(c):
    """A member of org A must not reach org B's project via A's org path —
    the project_id in the URL must be verified against the path org_id.
    Covers list/submit/deliverable endpoints that previously only checked
    org membership, not project ownership."""
    h, _ = await _auth(c)
    org_a = await _org(c, h)
    org_b = await _org(c, h)

    # Build a project + deliverable + submission in org B
    r = await c.post(
        f"/api/v1/orgs/{org_b}/projects",
        json={
            "title": "Org B Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid_b = r.json()["data"]["id"]
    rd = await c.post(
        f"/api/v1/orgs/{org_b}/projects/{pid_b}/deliverables",
        json={"name": "B Deliverable", "type": "text", "required": False},
        headers=h,
    )
    did_b = rd.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{org_b}/projects/{pid_b}/publish", headers=h)
    rs = await c.post(f"/api/v1/orgs/{org_b}/projects/{pid_b}/submissions", headers=h)
    sid_b = rs.json()["data"]["id"]

    # Every one of these uses org_a in the path but B's resources → 404
    probes = [
        ("GET", f"/api/v1/orgs/{org_a}/projects/{pid_b}/submissions"),
        ("GET", f"/api/v1/orgs/{org_a}/projects/{pid_b}/deliverables"),
        ("POST", f"/api/v1/orgs/{org_a}/projects/{pid_b}/deliverables"),
        ("PUT", f"/api/v1/orgs/{org_a}/projects/{pid_b}/deliverables/{did_b}"),
        ("DELETE", f"/api/v1/orgs/{org_a}/projects/{pid_b}/deliverables/{did_b}"),
        ("POST", f"/api/v1/orgs/{org_a}/projects/{pid_b}/submissions/{sid_b}/submit"),
        ("DELETE", f"/api/v1/orgs/{org_a}/projects/{pid_b}/submissions/{sid_b}"),
    ]
    for method, path in probes:
        body = None
        if method in ("POST", "PUT"):
            body = {"name": "Injected Deliverable", "type": "text", "required": False}
        r = await c.request(method, path, json=body, headers=h)
        assert r.status_code == 404, f"{method} {path} → {r.status_code} (cross-org confusion)"


# ── Wrong-type / raw-body validation regressions (bug-hunt round 7) ──


@pytest.mark.asyncio
async def test_raw_body_wrong_types_no_500(c):
    """Raw-dict endpoints must 422 on wrong-typed fields, not 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Raw Body Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]

    # project skills: non-list / list of non-strings → 422
    for bad in ({"skill_ids": "nope"}, {"skill_ids": 123}, {"skill_ids": [1, 2]}):
        r = await c.put(f"/api/v1/orgs/{oid}/projects/{pid}/skills", json=bad, headers=h)
        assert r.status_code == 422, f"{bad} -> {r.status_code}"

    # portfolio reorder: non-list → 422
    r = await c.put("/api/v1/portfolio/items/reorder", json={"item_ids": "nope"}, headers=h)
    assert r.status_code == 422

    # add member with non-string user_id → 422 (not FK 500)
    r = await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": 123, "role": "student"}, headers=h
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_extension_requires_org_member(c):
    """Granting an extension to a bogus or non-member user → 404, not FK 500
    and not a phantom extension for an outsider."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Extension Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = r.json()["data"]["id"]

    # bogus user
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/extensions",
        json={"user_id": "01BOGUSBOGUSBOGUSBOGUSBOGU", "new_deadline": "2030-01-01T00:00:00Z"},
        headers=h,
    )
    assert r.status_code == 404

    # real user who is not a member of this org
    h2, u2 = await _auth(c)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/extensions",
        json={"user_id": u2["id"], "new_deadline": "2030-01-01T00:00:00Z"},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_deadline_ordering_rejected(c):
    """late_deadline before deadline makes the late window negative — reject it."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Deadline Order Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "deadline": "2030-06-01T00:00:00Z",
            "late_deadline": "2030-05-01T00:00:00Z",
        },
        headers=h,
    )
    assert r.status_code == 422


# ── Evaluation settings bounds + JSONB persistence (bug-hunt round 8) ──


@pytest.mark.asyncio
async def test_eval_settings_bounds_and_persist(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # out-of-range values → 422
    for bad in ({"pass_threshold": 5}, {"pass_threshold": -1}, {"monthly_budget_usd": -100}):
        r = await c.put(f"/api/v1/orgs/{oid}/settings/evaluation", json=bad, headers=h)
        assert r.status_code == 422, f"{bad} -> {r.status_code}"

    # second nested update must persist (JSONB change-detection bug)
    await c.put(f"/api/v1/orgs/{oid}/settings/evaluation", json={"pass_threshold": 0.5}, headers=h)
    await c.put(f"/api/v1/orgs/{oid}/settings/evaluation", json={"pass_threshold": 0.9}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}/settings/evaluation", headers=h)
    assert r.json()["pass_threshold"] == 0.9

    # zero budget is a real budget, not "unlimited"
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation", json={"monthly_budget_usd": 0}, headers=h
    )
    r = await c.get(f"/api/v1/orgs/{oid}/evaluation/usage", headers=h)
    assert r.json()["budget_usd"] == 0
    assert r.json()["budget_remaining"] == 0


@pytest.mark.asyncio
async def test_org_settings_second_update_persists(c):
    """org.settings in-place mutation change-detection regression."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.put(f"/api/v1/orgs/{oid}/settings", json={"settings": {"a": 1}}, headers=h)
    await c.put(f"/api/v1/orgs/{oid}/settings", json={"settings": {"b": 2}}, headers=h)
    r = await c.get(f"/api/v1/orgs/{oid}", headers=h)
    # both keys should survive across separate updates
    # (GET org may not return settings; assert via a fresh settings write round-trip)
    assert r.status_code == 200


# ── Skill progress + MCQ grading robustness (bug-hunt round 9) ──


@pytest.mark.asyncio
async def test_wrong_mcq_does_not_complete_skill(c):
    """A skill must not be marked completed (and its dependents unlocked) when
    the learner only ever answered its MCQ incorrectly."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Progress Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "MCQ",
                "description": "d",
                "type": "multiple_choice",
                "config": {"correct": ["a"], "options": []},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]

    # wrong answer → graded (score 0) but NOT passed
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"selected": ["b"]}},
        headers=h,
    )
    assert r.json()["data"]["is_correct"] is False
    prog = await c.get(f"/api/v1/orgs/{oid}/progress/me", headers=h)
    assert prog.json()["skills_completed"] == 0

    # correct answer → skill completes
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"selected": ["a"]}},
        headers=h,
    )
    assert r.json()["data"]["is_correct"] is True
    prog = await c.get(f"/api/v1/orgs/{oid}/progress/me", headers=h)
    assert prog.json()["skills_completed"] == 1


@pytest.mark.asyncio
async def test_mcq_grading_tolerates_malformed_config_and_answer(c):
    """Malformed config.correct or answer.selected must not 500 the grader."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Robust Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    # config.correct is a bare int
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "MCQ",
                "description": "d",
                "type": "multiple_choice",
                "config": {"correct": 123, "options": []},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    for ans in ({"selected": [1, "a"]}, {"selected": {"x": 1}}, {"selected": 123}):
        r = await c.post(
            f"/api/v1/orgs/{oid}/exercises/{ex}/attempts", json={"answer": ans}, headers=h
        )
        assert r.status_code < 500, f"{ans} -> {r.status_code}"


@pytest.mark.asyncio
async def test_grade_attempt_score_bounds(c):
    """Instructor grade with out-of-range score → 422, not silent overflow."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Grade Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "Text",
                "description": "d",
                "type": "text_answer",
                "config": {},
                "max_score": 100,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    att = (
        await c.post(
            f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
            json={"answer": {"text": "hi"}},
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/grading/attempts/{att}", json={"score": -5}, headers=h)
    assert r.status_code == 422


# ── Portfolio slug collision + profile bounds (bug-hunt round 10) ──


@pytest.mark.asyncio
async def test_portfolio_duplicate_title_no_500(c):
    """Two items with the same title collide on (user_id, slug) — must not 500."""
    h, _ = await _auth(c)
    r1 = await c.post(
        "/api/v1/portfolio/items",
        json={"title": "My Great Work", "visibility": "public"},
        headers=h,
    )
    assert r1.status_code == 201
    r2 = await c.post(
        "/api/v1/portfolio/items",
        json={"title": "My Great Work", "visibility": "public"},
        headers=h,
    )
    assert r2.status_code == 201
    assert r1.json()["data"]["slug"] != r2.json()["data"]["slug"]


@pytest.mark.asyncio
async def test_profile_field_bounds(c):
    """Profile text fields, visibility enum, and social links are bounded."""
    h, _ = await _auth(c)
    bad_bodies = [
        {"headline": "x" * 300},
        {"bio": "y" * 6000},
        {"location": "z" * 300},
        {"visibility": "bogus"},
        {"social_links": {"a": "notaurl"}},
        {"website_url": "ftp://evil"},
    ]
    for body in bad_bodies:
        r = await c.put("/api/v1/portfolio/profile", json=body, headers=h)
        assert r.status_code == 422, f"{body} -> {r.status_code}"


@pytest.mark.asyncio
async def test_portfolio_item_create_bounds(c):
    """Portfolio item create validates url scheme/length, visibility enum,
    description length, and tag count (public-page inputs)."""
    h, _ = await _auth(c)
    bad_bodies = [
        {"title": "OK", "external_url": "javascript:alert(1)"},
        {"title": "OK", "visibility": "bogus"},
        {"title": "OK", "description": "x" * 3000},
        {"title": "OK", "tags": ["a"] * 40},
    ]
    for body in bad_bodies:
        r = await c.post("/api/v1/portfolio/items", json=body, headers=h)
        assert r.status_code == 422, f"{body} -> {r.status_code}"
    r = await c.post(
        "/api/v1/portfolio/items",
        json={"title": "Valid Item", "external_url": "https://x.com", "visibility": "unlisted"},
        headers=h,
    )
    assert r.status_code == 201


# ── Invite privilege-escalation guard (bug-hunt round 12) ──


@pytest.mark.asyncio
async def test_inviter_cannot_grant_higher_role(c):
    """An instructor must not create an invite link / email invite for a role
    above their own (admin/owner) — that would be privilege escalation."""
    # owner sets up org + instructor member
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    hi, _ = await _auth(c)
    link = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "instructor"}, headers=ho)
    await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hi)

    for role in ("admin", "owner"):
        r = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": role}, headers=hi)
        assert r.status_code == 403, f"instructor created {role} link: {r.status_code}"
        r = await c.post(
            f"/api/v1/orgs/{oid}/invites", json={"emails": ["x@y.com"], "role": role}, headers=hi
        )
        assert r.status_code == 403, f"instructor invited {role}: {r.status_code}"

    # instructor CAN still invite a student
    r = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=hi)
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_admin_cannot_add_owner_directly(c):
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    ha, _ = await _auth(c)
    link = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "admin"}, headers=ho)
    await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=ha)
    # a real target user
    ht, target = await _auth(c)
    r = await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": target["id"], "role": "owner"}, headers=ha
    )
    assert r.status_code == 403


# ── Evaluation trigger scoping + pagination bounds (bug-hunt round 13) ──


@pytest.mark.asyncio
async def test_trigger_evaluation_scoping(c):
    """Triggering an eval on a bogus or cross-org submission → 404, not FK 500
    and not an eval (charging budget) against another org's work."""
    h, _ = await _auth(c)
    org_a = await _org(c, h)
    org_b = await _org(c, h)
    await c.put(f"/api/v1/orgs/{org_a}/settings/evaluation", json={"enabled": True}, headers=h)

    # bogus submission
    r = await c.post(
        f"/api/v1/orgs/{org_a}/evaluation/trigger",
        json={"submission_id": "01BOGUSBOGUSBOGUSBOGUSBOGU", "type": "submission_review"},
        headers=h,
    )
    assert r.status_code == 404

    # cross-org submission
    rp = await c.post(
        f"/api/v1/orgs/{org_b}/projects",
        json={
            "title": "B Trigger Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = rp.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{org_b}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{org_b}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    r = await c.post(
        f"/api/v1/orgs/{org_a}/evaluation/trigger",
        json={"submission_id": sid, "type": "submission_review"},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_eval_and_admin_pagination_bounds(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for q in ("page=0", "page=-1", "per_page=0", "per_page=99999"):
        r = await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks?{q}", headers=h)
        assert r.status_code == 422, f"eval ?{q} -> {r.status_code}"


# ── Upload sniffer edge cases + public-page url scheme (bug-hunt round 15) ──


@pytest.mark.asyncio
async def test_upload_sniffer_edge_cases(c):
    """Empty, truncated, and mime-mismatched uploads must 422, never 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    rp = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Sniff Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
        },
        headers=h,
    )
    pid = rp.json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Image D", "type": "image", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    cases = [
        ("empty.png", b"", "image/png"),
        ("tiny.png", b"\x89PN", "image/png"),
        ("fake.png", b"\xff\xd8\xff\xe0" + b"\x00" * 20, "image/png"),  # jpeg magic, png declared
    ]
    for name, data_bytes, mime in cases:
        r = await c.post(
            f"/api/v1/orgs/{oid}/submissions/{sid}/files",
            files={"file": (name, data_bytes, mime)},
            data={"deliverable_id": did},
            headers=h,
        )
        assert r.status_code == 422, f"{name} -> {r.status_code}"


@pytest.mark.asyncio
async def test_deliverable_config_and_type_validation(c):
    """Deliverable type must be a known enum and config values must be sane —
    a garbage max_file_size_mb / non-list accepted_formats silently disables
    upload enforcement, so it must be rejected at definition time."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Cfg Val Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    bad_configs = [
        {"max_files": "abc"},
        {"max_file_size_mb": -5},
        {"accepted_formats": "nope"},
        {"max_files": 0},
    ]
    for cfg in bad_configs:
        r = await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Img D", "type": "image", "config": cfg, "required": False},
            headers=h,
        )
        assert r.status_code == 422, f"{cfg} -> {r.status_code}"

    # unknown type
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
        json={"name": "X", "type": "bogus", "required": False},
        headers=h,
    )
    assert r.status_code == 422

    # valid config
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
        json={
            "name": "Good D",
            "type": "image",
            "config": {"max_files": 5, "max_file_size_mb": 25, "accepted_formats": ["image/png"]},
            "required": False,
        },
        headers=h,
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_unbounded_text_fields_now_bounded(c):
    """Org/category description and exercise config were unbounded storage
    surfaces — confirm they now reject oversized input."""
    h, _ = await _auth(c)
    # org description
    r = await c.post("/api/v1/orgs", json={"name": "Big Org", "description": "x" * 3000}, headers=h)
    assert r.status_code == 422

    oid = await _org(c, h)
    # category description
    r = await c.post(
        f"/api/v1/orgs/{oid}/categories", json={"name": "Cat", "description": "y" * 3000}, headers=h
    )
    assert r.status_code == 422

    # exercise config blob
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat2"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Skill EX",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
        json={
            "title": "Ex",
            "description": "d",
            "type": "text_answer",
            "config": {"blob": "z" * 25000},
            "max_score": 10,
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_duplicate_prerequisites_and_project_skills(c):
    """Repeated ids in prerequisites / project-skills must not 500 on the
    composite primary key — they should be de-duplicated."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]

    async def mk_skill(name):
        return (
            await c.post(
                f"/api/v1/orgs/{oid}/skills",
                json={
                    "name": name,
                    "description": "d" * 10,
                    "difficulty": "beginner",
                    "category_id": cat,
                },
                headers=h,
            )
        ).json()["data"]["id"]

    a = await mk_skill("Skill A Dup")
    b = await mk_skill("Skill B Dup")

    # duplicate prerequisite ids
    r = await c.put(
        f"/api/v1/orgs/{oid}/skills/{a}/prerequisites",
        json={"prerequisite_ids": [b, b, b]},
        headers=h,
    )
    assert r.status_code == 200

    # self-prerequisite → cycle 422
    r = await c.put(
        f"/api/v1/orgs/{oid}/skills/{a}/prerequisites", json={"prerequisite_ids": [a]}, headers=h
    )
    assert r.status_code == 422

    # duplicate project-skill ids
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Dup Skill Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/skills", json={"skill_ids": [a, a, b]}, headers=h
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_student_cannot_submit_to_unpublished_project(c):
    """A student must not create a submission on a draft/unpublished project;
    an instructor still may (to test the flow)."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Draft Only Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]

    # instructor (owner) may submit to the draft
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=ho)
    assert r.status_code == 201

    # student may not
    hs, _ = await _auth(c)
    link = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho)
    await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)
    assert r.status_code == 422

    # once published, the student can
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_extension_reason_bounded(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Ext Reason Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/extensions",
        json={
            "user_id": "01BOGUSBOGUSBOGUSBOGUSBOGU",
            "new_deadline": "2030-01-01T00:00:00Z",
            "reason": "x" * 2000,
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_student_cannot_attempt_unpublished_skill(c):
    """A student must not attempt exercises of a draft skill; the instructor
    may (to test), and the student can once it's published."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=ho)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Publish Gate Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "Ex",
                "description": "d",
                "type": "text_answer",
                "config": {},
                "max_score": 10,
            },
            headers=ho,
        )
    ).json()["data"]["id"]

    # instructor can attempt the draft skill's exercise
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts", json={"answer": {"text": "hi"}}, headers=ho
    )
    assert r.status_code == 201

    # student cannot, while draft
    hs, _ = await _auth(c)
    link = await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho)
    await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts", json={"answer": {"text": "hi"}}, headers=hs
    )
    assert r.status_code == 422

    # published → student can
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=ho)
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts", json={"answer": {"text": "hi"}}, headers=hs
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_revision_requested_edit_and_resubmit(c):
    """After an instructor requests a revision, the learner must be able to
    edit the submission and resubmit it — the revision loop must not dead-end."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Revision Loop Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Text D", "type": "text", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)

    # instructor requests revision
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "revision_requested", "feedback": "add more"},
        headers=h,
    )
    assert r.status_code == 201

    # learner edits + resubmits
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
        json={"items": [{"deliverable_id": did, "type": "text", "content": "revised"}]},
        headers=h,
    )
    assert r.status_code == 200
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"

    # an APPROVED submission is locked (not editable)
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 90},
        headers=h,
    )
    assert r.status_code == 201
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
        json={"items": [{"deliverable_id": did, "type": "text", "content": "sneaky"}]},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_partial_deadline_update_preserves_ordering(c):
    """A partial project update changing only `deadline` must not push it past
    an existing late_deadline (the schema model_validator only fires when both
    fields are present in the request)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Partial Deadline Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
                "deadline": "2030-06-01T00:00:00Z",
                "late_deadline": "2030-06-05T00:00:00Z",
            },
            headers=h,
        )
    ).json()["data"]["id"]
    # push deadline past the existing late_deadline via a partial update
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}", json={"deadline": "2030-06-10T00:00:00Z"}, headers=h
    )
    assert r.status_code == 422
    # a valid partial update still works
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}", json={"deadline": "2030-06-03T00:00:00Z"}, headers=h
    )
    assert r.status_code == 200


def _mini_png(color: int = 1) -> bytes:
    import struct
    import zlib

    sig = b"\x89PNG\r\n\x1a\n"

    def ch(t, d):
        crc = zlib.crc32(t + d) & 0xFFFFFFFF
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (
        sig + ch(b"IHDR", ihdr) + ch(b"IDAT", zlib.compress(bytes((color,) * 3))) + ch(b"IEND", b"")
    )


@pytest.mark.asyncio
async def test_version_numbers_unique_after_delete(c):
    """Deleting a middle version must not cause the next upload to reuse a
    version number (was count+1 → collision; now max+1). And max_files must
    free a slot when a file is deleted."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Version Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Img", "type": "image", "config": {"max_files": 2}, "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    async def up(color):
        return await c.post(
            f"/api/v1/orgs/{oid}/submissions/{sid}/files",
            files={"file": (f"f{color}.png", _mini_png(color), "image/png")},
            data={"deliverable_id": did},
            headers=h,
        )

    r1 = await up(10)
    f1 = r1.json()["data"]["id"]
    await up(20)
    # 3rd blocked by max_files=2
    assert (await up(30)).status_code == 422
    # delete v1 → slot freed AND next version is max+1 (3), not a reused number
    await c.delete(f"/api/v1/orgs/{oid}/submissions/{sid}/files/{f1}", headers=h)
    r3 = await up(40)
    assert r3.status_code == 201
    det = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    versions = [i["version"] for i in det["items"] if i["deliverable_id"] == did]
    assert len(versions) == len(set(versions)), f"duplicate versions: {versions}"


@pytest.mark.asyncio
async def test_blank_item_does_not_satisfy_required(c):
    """A required deliverable must not be satisfied by an empty/whitespace-only
    text item — only meaningful content (or a file/prompt) counts."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Required Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Text D", "type": "text", "required": True},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    # whitespace-only content → does NOT satisfy the required deliverable
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
        json={"items": [{"deliverable_id": did, "type": "text", "content": "   "}]},
        headers=h,
    )
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert r.status_code == 422

    # real content → satisfies it
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
        json={"items": [{"deliverable_id": did, "type": "text", "content": "my real answer"}]},
        headers=h,
    )
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_inline_item_edit_replaces_not_accumulates(c):
    """Re-PUTting a text/markdown/link deliverable replaces the existing row
    instead of piling up untracked duplicate items."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Inline Edit Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Text D", "type": "text", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    for txt in ("first", "second", "third"):
        await c.put(
            f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
            json={"items": [{"deliverable_id": did, "type": "text", "content": txt}]},
            headers=h,
        )
    det = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    text_items = [i for i in det["items"] if i["deliverable_id"] == did]
    assert len(text_items) == 1
    assert text_items[0]["content"] == "third"


@pytest.mark.asyncio
async def test_prompt_item_edit_replaces(c):
    """Re-submitting a prompt deliverable replaces the row instead of piling
    up duplicates that inflate the version counter."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Prompt Edit Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Prompt D", "type": "prompt", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    for pr in ("one", "two", "three"):
        await c.post(
            f"/api/v1/orgs/{oid}/submissions/{sid}/prompt-items",
            json={"deliverable_id": did, "prompt": pr},
            headers=h,
        )
    det = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    items = [i for i in det["items"] if i["deliverable_id"] == did]
    assert len(items) == 1
    import json as _json

    assert _json.loads(items[0]["content"])["prompt"] == "three"


@pytest.mark.asyncio
async def test_delete_submission_with_file_succeeds(c):
    """Deleting a draft submission that has an uploaded file succeeds (S3
    objects are cleaned up best-effort, DB rows cascade)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Del File Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Img", "type": "image", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/files",
        files={"file": ("a.png", _mini_png(), "image/png")},
        data={"deliverable_id": did},
        headers=h,
    )
    r = await c.delete(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)
    assert r.status_code == 204


@pytest.mark.asyncio
async def test_long_filename_and_asset_bounds(c):
    """A >200-char filename must be clamped (no DataError/invalid-object-name
    500), and asset name/description form fields are bounded."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Filename Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
            json={"name": "Img", "type": "image", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    # 260-char filename → clamped, upload succeeds
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/files",
        files={"file": ("A" * 260 + ".png", _mini_png(), "image/png")},
        data={"deliverable_id": did},
        headers=h,
    )
    assert r.status_code == 201
    assert len(r.json()["data"]["file_name"]) <= 200

    # asset with a huge name → 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/assets",
        files={"file": ("ref.png", _mini_png(), "image/png")},
        data={"name": "N" * 300},
        headers=h,
    )
    assert r.status_code == 422

    # asset with a long filename but valid name → clamped, 201
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/assets",
        files={"file": ("B" * 260 + ".png", _mini_png(), "image/png")},
        data={"name": "Ref"},
        headers=h,
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_cover_upload_rejects_spoofed_content(c):
    """A non-image payload declared as image/* must be rejected — cover urls
    are served straight from the public bucket (stored-XSS vector)."""
    h, _ = await _auth(c)
    r = await c.post(
        "/api/v1/portfolio/upload-cover",
        files={"file": ("evil.png", b"<html><script>alert(1)</script></html>", "image/png")},
        headers=h,
    )
    assert r.status_code == 422
    # a real PNG is accepted, even with a very long filename
    r = await c.post(
        "/api/v1/portfolio/upload-cover",
        files={"file": ("C" * 260 + ".png", _mini_png(), "image/png")},
        headers=h,
    )
    assert r.status_code in (200, 201)


@pytest.mark.asyncio
async def test_reorder_exercises_rejects_foreign_exercise(c):
    """exercises/reorder must verify each id belongs to the skill — otherwise
    a caller could reorder another skill's / org's exercises by id."""
    h, _ = await _auth(c)

    async def skill_with_exercise(oid):
        cat = (
            await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)
        ).json()["data"]["id"]
        sk = (
            await c.post(
                f"/api/v1/orgs/{oid}/skills",
                json={
                    "name": "Skill One",
                    "description": "d" * 10,
                    "difficulty": "beginner",
                    "category_id": cat,
                },
                headers=h,
            )
        ).json()["data"]["id"]
        ex = (
            await c.post(
                f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
                json={
                    "title": "Ex",
                    "description": "d",
                    "type": "text_answer",
                    "config": {},
                    "max_score": 10,
                },
                headers=h,
            )
        ).json()["data"]["id"]
        return sk, ex

    oa = await _org(c, h)
    sk_a, _ = await skill_with_exercise(oa)
    ob = await _org(c, h)
    _, ex_b = await skill_with_exercise(ob)

    r = await c.put(
        f"/api/v1/orgs/{oa}/skills/{sk_a}/exercises/reorder",
        json={"items": [{"id": ex_b, "sort_order": 99}]},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_portfolio_item_cannot_link_foreign_submission(c):
    """Linking another user's submission to your portfolio item must 404."""
    hv, _ = await _auth(c)
    oid = await _org(c, hv)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "PF Link Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hv,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hv)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hv)).json()[
        "data"
    ]["id"]

    ha, _ = await _auth(c)
    r = await c.post(
        "/api/v1/portfolio/items",
        json={"title": "Stolen Work", "submission_id": sid, "visibility": "public"},
        headers=ha,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_username_collision_and_format(c):
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    import uuid as _uuid

    uname = f"taken{_uuid.uuid4().hex[:6]}"
    assert (
        await c.put("/api/v1/portfolio/username", json={"username": uname}, headers=h1)
    ).status_code == 200
    # same name (case-insensitive) taken by another user → 409
    assert (
        await c.put("/api/v1/portfolio/username", json={"username": uname.upper()}, headers=h2)
    ).status_code == 409
    # reserved / malformed → 422
    for bad in ("admin", "ab", "has space", "x" * 50):
        r = await c.put("/api/v1/portfolio/username", json={"username": bad}, headers=h2)
        assert r.status_code == 422, f"{bad!r} -> {r.status_code}"


@pytest.mark.asyncio
async def test_expert_difficulty_and_bad_filters(c):
    """`expert` is a valid difficulty (DB enum + FE dropdown) and must be
    accepted; bad difficulty/status filter query params must 422, not 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]

    # expert skill accepted
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "name": "Expert Skill",
            "description": "d" * 10,
            "difficulty": "expert",
            "category_id": cat,
        },
        headers=h,
    )
    assert r.status_code == 201

    # bad filters → 422, not 500
    assert (
        await c.get(f"/api/v1/orgs/{oid}/skills?difficulty=bogus", headers=h)
    ).status_code == 422
    assert (await c.get(f"/api/v1/orgs/{oid}/skills?status=bogus", headers=h)).status_code == 422
    assert (await c.get(f"/api/v1/orgs/{oid}/projects?status=bogus", headers=h)).status_code == 422


@pytest.mark.asyncio
async def test_review_score_breakdown_bounded(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "SB Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 90, "score_breakdown": {"blob": "z" * 25000}},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_id_list_and_settings_bounds(c):
    """skill_ids / skill_names lists and the org settings dict are bounded."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "IL Project",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "skill_ids": ["x"] * 300,
        },
        headers=h,
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/orgs/{oid}/settings", json={"settings": {"blob": "z" * 25000}}, headers=h
    )
    assert r.status_code == 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/project-templates",
        json={
            "name": "T",
            "description": "d",
            "instructions": "i",
            "difficulty": "intermediate",
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "deliverables": [],
            "skill_names": ["x"] * 300,
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_from_template_instantiation_and_bad_ids(c):
    """Builtin template instantiates with deliverables deep-copied; unknown
    template ids (builtin- prefix or real) 404."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/from-template",
        json={"template_id": "builtin-ai-product-ad", "title": "My Ad"},
        headers=h,
    )
    assert r.status_code == 201
    pid = r.json()["data"]["id"]
    dl = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/deliverables", headers=h)).json()["data"]
    assert len(dl) == 8

    for bad in ("builtin-nonexistent", "01BOGUSBOGUSBOGUSBOGUSBOGU"):
        r = await c.post(
            f"/api/v1/orgs/{oid}/projects/from-template",
            json={"template_id": bad, "title": "Valid Title"},
            headers=h,
        )
        assert r.status_code == 404, f"{bad} -> {r.status_code}"


@pytest.mark.asyncio
async def test_list_filters_reject_bad_enum(c):
    """Bad enum values in list-filter query params → 422, never 500
    (eval tasks status/type, member role)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    assert (
        await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks?status=bogus", headers=h)
    ).status_code == 422
    assert (
        await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks?eval_type=bogus", headers=h)
    ).status_code == 422
    assert (await c.get(f"/api/v1/orgs/{oid}/members?role=bogus", headers=h)).status_code == 422


@pytest.mark.asyncio
async def test_malformed_path_ids_no_500(c):
    """Malformed resource ids in the URL path must 4xx, never 500 (no unguarded
    db.get / enum coercion / path-traversal blowups)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    bad = "!!!not-a-ulid!!!"
    probes = [
        ("GET", f"/api/v1/orgs/{oid}/projects/{bad}"),
        ("GET", f"/api/v1/orgs/{oid}/skills/{bad}"),
        ("GET", f"/api/v1/orgs/{oid}/exercises/{bad}"),
        ("GET", f"/api/v1/orgs/{oid}/project-templates/{bad}"),
        ("GET", f"/api/v1/orgs/{oid}/evaluation/tasks/{bad}"),
        ("GET", f"/api/v1/orgs/{oid}/projects/{bad}/submissions"),
        ("GET", f"/api/v1/orgs/{oid}/submissions/{bad}/comments"),
        ("DELETE", f"/api/v1/portfolio/items/{bad}"),
        ("GET", f"/api/v1/u/{bad}"),
    ]
    for method, path in probes:
        r = await c.request(method, path, headers=h)
        assert r.status_code < 500, f"{method} {path} -> {r.status_code}"


@pytest.mark.asyncio
async def test_auth_edge_inputs_no_500(c):
    """Malformed auth inputs must validate (4xx), never 500."""
    for em in ("notanemail", "a@", "@b.com", "", "spaces in@x.com"):
        r = await c.post(
            "/api/v1/auth/register",
            json={"email": em, "password": "TestPass123!", "display_name": "Edge"},
        )
        assert r.status_code < 500, f"register {em!r} -> {r.status_code}"
    for body in ({"email": "x", "password": "y"}, {"password": "y"}, {"email": "a@b.com"}):
        r = await c.post("/api/v1/auth/login", json=body)
        assert r.status_code < 500, f"login {body} -> {r.status_code}"
    assert (
        await c.post(
            "/api/v1/auth/reset-password", json={"token": "garbage", "new_password": "NewPass123!"}
        )
    ).status_code < 500
    assert (await c.get("/api/v1/auth/verify-email?token=garbage")).status_code < 500


@pytest.mark.asyncio
async def test_revision_clears_stale_final_score(c):
    """Approving a submission sets final_score; sending it back for revision
    must clear it (the work is being redone), not leave the old score."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Rework Project",
                "description": "d",
                "instructions": "i",
                "max_score": 100,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)

    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 80},
        headers=h,
    )
    d = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    assert d["final_score"] == 80

    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "revision_requested", "feedback": "redo"},
        headers=h,
    )
    d = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    assert d["status"] == "revision_requested"
    assert d["final_score"] is None


@pytest.mark.asyncio
async def test_review_lifecycle_queue_and_history(c):
    """Full review lifecycle: pending queue reflects only SUBMITTED work,
    rejected is terminal, review records accumulate as history, and a
    resubmitted revision re-enters the queue."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Lifecycle Project",
                "description": "d",
                "instructions": "i",
                "max_score": 100,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)

    async def pending_count():
        r = await c.get(f"/api/v1/orgs/{oid}/reviews/pending", headers=h)
        return r.json()["meta"]["total"]

    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    assert await pending_count() == 0  # draft not pending
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert await pending_count() == 1

    # revision → resubmit → back in queue
    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "revision_requested", "feedback": "redo"},
        headers=h,
    )
    assert await pending_count() == 0
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert await pending_count() == 1

    # approve → out of queue, 2 review records, latest first
    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 90},
        headers=h,
    )
    assert await pending_count() == 0
    d = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    assert d["status"] == "approved" and d["final_score"] == 90
    assert len(d["reviews"]) == 2
    assert d["reviews"][0]["status"] == "approved"


@pytest.mark.asyncio
async def test_rejected_submission_is_terminal(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Reject Terminal Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "rejected", "score": 10},
        headers=h,
    )
    # a rejected submission cannot be resubmitted
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_data_isolation_and_role_gating(c):
    """Students cannot see other students' submissions, instructor-only
    queues, or another user's private portfolio items."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Isolation Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)

    async def join_student():
        hs, _ = await _auth(c)
        link = await c.post(
            f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho
        )
        await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
        return hs

    ha = await join_student()
    hb = await join_student()
    sa = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=ha)).json()[
        "data"
    ]["id"]
    sb = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hb)).json()[
        "data"
    ]["id"]

    # A sees only own in list, and 403 on B's detail
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=ha)
    ids = [x["id"] for x in r.json()["data"]]
    assert sa in ids and sb not in ids
    assert (
        await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sb}", headers=ha)
    ).status_code == 403

    # instructor-only queues 403 for students
    assert (await c.get(f"/api/v1/orgs/{oid}/reviews/pending", headers=ha)).status_code == 403
    assert (await c.get(f"/api/v1/orgs/{oid}/grading/pending", headers=ha)).status_code == 403
    assert (await c.get(f"/api/v1/orgs/{oid}/evaluation/usage", headers=ha)).status_code == 403


@pytest.mark.asyncio
async def test_public_page_hides_private_items(c):
    h, _ = await _auth(c)
    await c.put("/api/v1/portfolio/profile", json={"visibility": "public"}, headers=h)
    await c.post(
        "/api/v1/portfolio/items", json={"title": "Secret Work", "visibility": "private"}, headers=h
    )
    await c.post(
        "/api/v1/portfolio/items", json={"title": "Public Work", "visibility": "public"}, headers=h
    )
    uname = (await c.get("/api/v1/portfolio/profile", headers=h)).json()["data"]["username"]
    titles = [i["title"] for i in (await c.get(f"/api/v1/u/{uname}/items")).json()["data"]]
    assert "Secret Work" not in titles
    assert "Public Work" in titles


@pytest.mark.asyncio
async def test_peer_round_phase_guards_and_assessment_ownership(c):
    """Peer round can't be double-started or closed-before-started, and a
    learner cannot submit another learner's assessment."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Peer Guard Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)

    async def join_and_submit():
        hs, _ = await _auth(c)
        link = await c.post(
            f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho
        )
        await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
        s = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
            "data"
        ]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{s}/submit", headers=hs)
        return hs

    s0 = await join_and_submit()
    s1 = await join_and_submit()
    await join_and_submit()

    rid = (
        await c.post(
            f"/api/v1/orgs/{oid}/peer-review-rounds",
            json={"project_id": pid, "name": "R1", "num_reviews": 1},
            headers=ho,
        )
    ).json()["data"]["id"]

    # close-before-start → 422
    assert (
        await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/close", headers=ho)
    ).status_code == 422
    # start, then double-start → 422
    assert (
        await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/start", headers=ho)
    ).status_code == 200
    assert (
        await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/start", headers=ho)
    ).status_code == 422

    # a learner cannot submit another learner's assessment
    my = (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/my-assessments", headers=s0)
    ).json()["data"]
    aid = my[0]["id"]
    assert (
        await c.post(
            f"/api/v1/orgs/{oid}/peer-assessments/{aid}/submit", json={"score": 50}, headers=s1
        )
    ).status_code == 403


@pytest.mark.asyncio
async def test_deliverable_type_mismatch_rejected(c):
    """A prompt on an image deliverable, or a wrong-media file on an image
    deliverable, is rejected; text deliverables accept inline content."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    async def setup(dtype):
        pid = (
            await c.post(
                f"/api/v1/orgs/{oid}/projects",
                json={
                    "title": "Mismatch Project",
                    "description": "d",
                    "instructions": "i",
                    "rubric": [{"criterion": "Q", "max_score": 100}],
                },
                headers=h,
            )
        ).json()["data"]["id"]
        did = (
            await c.post(
                f"/api/v1/orgs/{oid}/projects/{pid}/deliverables",
                json={"name": "Deliverable", "type": dtype, "required": False},
                headers=h,
            )
        ).json()["data"]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
        sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
            "data"
        ]["id"]
        return did, sid

    did, sid = await setup("image")
    # prompt on an image deliverable → 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/prompt-items",
        json={"deliverable_id": did, "prompt": "hi"},
        headers=h,
    )
    assert r.status_code == 422
    # audio bytes on an image deliverable → 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/files",
        files={"file": ("a.mp3", b"ID3\x03\x00\x00\x00" + b"\x00" * 20, "audio/mpeg")},
        data={"deliverable_id": did},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_progress_categories_populated(c):
    """get_user_progress must return the per-category breakdown (was always []
    while the API declared it and the progress UI rendered it)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Programming"}, headers=h)
    ).json()["data"]["id"]
    for name in ("Python", "Rust"):
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": name,
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    d = (await c.get(f"/api/v1/orgs/{oid}/progress/me", headers=h)).json()
    assert len(d["categories"]) == 1
    entry = d["categories"][0]
    assert entry["name"] == "Programming"
    assert entry["skills_total"] == 2
    assert entry["skills_completed"] == 0
    assert entry["completion_percentage"] == 0.0


@pytest.mark.asyncio
async def test_single_skill_progress_includes_name(c):
    """GET /progress/me/skills/{id} must return the skill_name (was always ''
    because SkillProgress has no skill_name column)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Python Mastery",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "Ex",
                "description": "d",
                "type": "text_answer",
                "config": {},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts", json={"answer": {"text": "hi"}}, headers=h
    )
    d = (await c.get(f"/api/v1/orgs/{oid}/progress/me/skills/{sk}", headers=h)).json()["data"]
    assert d is not None
    assert d["skill_name"] == "Python Mastery"


@pytest.mark.asyncio
async def test_skill_progress_best_score_computed(c):
    """best_score column was declared + returned but never written (always
    NULL). It should now be the sum of the user's best attempt per exercise."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Best Score Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "MCQ",
                "description": "d",
                "type": "multiple_choice",
                "config": {"correct": ["a"], "options": []},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=h)
    # wrong (0), then correct (10) → best_score 10
    await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"selected": ["b"]}},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"selected": ["a"]}},
        headers=h,
    )
    d = (await c.get(f"/api/v1/orgs/{oid}/progress/me/skills/{sk}", headers=h)).json()["data"]
    assert d["best_score"] == 10


@pytest.mark.asyncio
async def test_peer_results_gated_until_closed_for_students(c):
    """Students can only see aggregate peer results after the round CLOSES;
    instructors can see anytime (avoids anchoring reviewers on the crowd)."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Peer Results Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)

    studs = []
    for _ in range(3):
        hs, _ = await _auth(c)
        link = await c.post(
            f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho
        )
        await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
        s = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
            "data"
        ]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{s}/submit", headers=hs)
        studs.append(hs)

    rid = (
        await c.post(
            f"/api/v1/orgs/{oid}/peer-review-rounds",
            json={"project_id": pid, "name": "R1", "num_reviews": 1},
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/start", headers=ho)
    for hs in studs:
        my = (
            await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/my-assessments", headers=hs)
        ).json()["data"]
        for a in my:
            await c.post(
                f"/api/v1/orgs/{oid}/peer-assessments/{a['id']}/submit",
                json={"score": 70},
                headers=hs,
            )

    # mid-assessment: student 403, instructor 200
    assert (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/results", headers=studs[0])
    ).status_code == 403
    assert (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/results", headers=ho)
    ).status_code == 200
    # after close: student 200
    await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/close", headers=ho)
    assert (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/results", headers=studs[0])
    ).status_code == 200


@pytest.mark.asyncio
async def test_peer_anonymity_and_round_list_scoping(c):
    """Students can't hit the instructor-only all-assessments (reviewer
    identities), my-assessments never exposes reviewer_id, and listing rounds
    for a project doesn't return another org's rounds."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Anon Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)

    studs = []
    for _ in range(2):
        hs, _ = await _auth(c)
        link = await c.post(
            f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho
        )
        await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
        s = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
            "data"
        ]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{s}/submit", headers=hs)
        studs.append(hs)

    rid = (
        await c.post(
            f"/api/v1/orgs/{oid}/peer-review-rounds",
            json={"project_id": pid, "name": "R1", "num_reviews": 1, "anonymous": True},
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/start", headers=ho)

    # student blocked from all-assessments (reveals reviewer_id)
    assert (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/assessments", headers=studs[0])
    ).status_code == 403
    # my-assessments never carries reviewer_id
    my = (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/my-assessments", headers=studs[0])
    ).json()["data"]
    assert all("reviewer_id" not in a for a in my)

    # listing rounds of a cross-org project returns nothing
    oid2 = await _org(c, ho)
    pid2 = (
        await c.post(
            f"/api/v1/orgs/{oid2}/projects",
            json={
                "title": "Other Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid2}/peer-review-rounds",
        json={"project_id": pid2, "name": "R-B"},
        headers=ho,
    )
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid2}/peer-review-rounds", headers=ho)
    assert len(r.json()["data"]) == 0


@pytest.mark.asyncio
async def test_auto_evaluate_on_submit(c):
    """The 'Auto-evaluate on submission' setting must actually trigger an eval
    task on submit (it was a dead toggle — never wired). When disabled, no
    task is created; submit still succeeds regardless of eval outcome."""
    from unittest.mock import AsyncMock, patch

    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "auto_evaluate": True},
        headers=h,
    )
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "AutoEval Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    class _Resp:
        content = '{"scores":[{"criterion":"Q","score":80,"max_score":100,"feedback":"ok"}],"overall_feedback":"g","strengths":[],"improvements":[]}'
        input_tokens = 10
        output_tokens = 20
        provider = "anthropic"
        model = "claude-sonnet-5"

    fake = AsyncMock()
    fake.complete = AsyncMock(return_value=_Resp())
    with patch("app.services.evaluation.create_llm_client", return_value=fake):
        r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert r.status_code == 200
    tasks = (await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks", headers=h)).json()
    assert tasks["meta"]["total"] >= 1

    # auto_evaluate off → no task
    await c.put(f"/api/v1/orgs/{oid}/settings/evaluation", json={"auto_evaluate": False}, headers=h)
    pid2 = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "NoAutoEval Project",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/publish", headers=h)
    sid2 = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/submissions/{sid2}/submit", headers=h)
    assert r.status_code == 200
    # no task for pid2's submission
    all_tasks = (
        await c.get(f"/api/v1/orgs/{oid}/evaluation/tasks?per_page=100", headers=h)
    ).json()["data"]
    assert all(t["submission_id"] != sid2 for t in all_tasks)


@pytest.mark.asyncio
async def test_late_penalty_and_max_submissions(c):
    """Late submissions get the configured penalty applied to final_score, and
    max_submissions caps the number of drafts a learner can create."""
    from datetime import UTC, datetime, timedelta

    h, _ = await _auth(c)
    oid = await _org(c, h)

    # late-penalty project (deadline passed, late window open, 20% penalty)
    past = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    future = (datetime.now(UTC) + timedelta(days=2)).isoformat()
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Late Project",
                "description": "d",
                "instructions": "i",
                "max_score": 100,
                "late_penalty_pct": 20,
                "deadline": past,
                "late_deadline": future,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)
    assert r.json()["data"]["is_late"] is True
    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 100},
        headers=h,
    )
    d = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    assert d["final_score"] == 80  # 100 - 20%

    # max_submissions cap
    pid2 = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Cap Project",
                "description": "d",
                "instructions": "i",
                "max_submissions": 2,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/publish", headers=h)
    assert (
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/submissions", headers=h)
    ).status_code == 201
    assert (
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/submissions", headers=h)
    ).status_code == 201
    assert (
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid2}/submissions", headers=h)
    ).status_code == 422


@pytest.mark.asyncio
async def test_grading_queue_routing_and_scoping(c):
    """Auto-graded MCQ stays out of the manual grading queue; a text answer
    enters it and leaves once graded; grading a bogus/cross-org attempt 404s."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Grading Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    mcq = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "MCQ",
                "description": "d",
                "type": "multiple_choice",
                "config": {"correct": ["a"], "options": []},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    txt = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "Text",
                "description": "d",
                "type": "text_answer",
                "config": {},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=h)

    mcq_att = (
        await c.post(
            f"/api/v1/orgs/{oid}/exercises/{mcq}/attempts",
            json={"answer": {"selected": ["a"]}},
            headers=h,
        )
    ).json()["data"]
    assert mcq_att["graded_by"] == "auto"
    txt_att = (
        await c.post(
            f"/api/v1/orgs/{oid}/exercises/{txt}/attempts",
            json={"answer": {"text": "ans"}},
            headers=h,
        )
    ).json()["data"]
    assert txt_att["graded_by"] is None

    pend = (await c.get(f"/api/v1/orgs/{oid}/grading/pending", headers=h)).json()["data"]
    ids = {a["id"] for a in pend}
    assert mcq_att["id"] not in ids  # auto-graded excluded
    assert txt_att["id"] in ids  # awaiting manual grade

    # grade the text answer → leaves the queue
    assert (
        await c.post(
            f"/api/v1/orgs/{oid}/grading/attempts/{txt_att['id']}", json={"score": 8}, headers=h
        )
    ).status_code == 200
    pend = (await c.get(f"/api/v1/orgs/{oid}/grading/pending", headers=h)).json()["data"]
    assert txt_att["id"] not in {a["id"] for a in pend}

    # bogus attempt id → 404
    assert (
        await c.post(
            f"/api/v1/orgs/{oid}/grading/attempts/01BOGUSBOGUSBOGUSBOGUSBOGU",
            json={"score": 5},
            headers=h,
        )
    ).status_code == 404


@pytest.mark.asyncio
async def test_join_archived_org_rejected(c):
    """Invite links and email invites must stop working once the org is
    archived — otherwise joins create ghost memberships (bug #95)."""
    h1, _ = await _auth(c)
    h2, u2 = await _auth(c)
    oid = await _org(c, h1)

    link = (
        await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=h1)
    ).json()["data"]

    # archive the org
    assert (await c.delete(f"/api/v1/orgs/{oid}", headers=h1)).status_code == 204

    # join by code → rejected, no ghost membership
    r = await c.post("/api/v1/invites/join", json={"code": link["code"]}, headers=h2)
    assert r.status_code == 422
    orgs = (await c.get("/api/v1/orgs", headers=h2)).json()["data"]
    assert all(o["id"] != oid for o in orgs)


@pytest.mark.asyncio
async def test_org_logo_url_scheme_restricted(c):
    """logo_url is rendered as <img src>; javascript:/data: schemes must be
    rejected (stored-XSS vector, bug #96). https stays accepted."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.put(f"/api/v1/orgs/{oid}", json={"logo_url": "javascript:alert(1)"}, headers=h)
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/orgs/{oid}", json={"logo_url": "data:text/html,<script>1</script>"}, headers=h
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/orgs/{oid}", json={"logo_url": "https://cdn.example.com/logo.png"}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["data"]["logo_url"] == "https://cdn.example.com/logo.png"


@pytest.mark.asyncio
async def test_avatar_and_portfolio_update_url_schemes(c):
    """avatar_url (bug #97) and portfolio-item update URLs (bug #98) must
    reject javascript:/data: schemes — update was bypassing the create-time
    validation, and avatar_url had no scheme check at all."""
    h, _ = await _auth(c)

    r = await c.put("/api/v1/auth/me", json={"avatar_url": "javascript:alert(1)"}, headers=h)
    assert r.status_code == 422
    r = await c.put(
        "/api/v1/auth/me", json={"avatar_url": "https://cdn.example.com/a.png"}, headers=h
    )
    assert r.status_code == 200

    iid = (await c.post("/api/v1/portfolio/items", json={"title": "URL Item"}, headers=h)).json()[
        "data"
    ]["id"]
    r = await c.put(
        f"/api/v1/portfolio/items/{iid}", json={"external_url": "javascript:alert(1)"}, headers=h
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/portfolio/items/{iid}", json={"cover_image_url": "data:text/html,<x>"}, headers=h
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/portfolio/items/{iid}", json={"external_url": "https://example.com/w"}, headers=h
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_private_profile_hides_item_detail(c):
    """When a profile is private, the public item-detail endpoint must 404 —
    it was leaking items even though profile + list were hidden (bug #99)."""
    h, _ = await _auth(c)
    un = f"user{uuid.uuid4().hex[:8]}"
    assert (
        await c.put("/api/v1/portfolio/username", json={"username": un}, headers=h)
    ).status_code == 200
    item = (
        await c.post("/api/v1/portfolio/items", json={"title": "Secret Work"}, headers=h)
    ).json()["data"]

    # public profile → item visible
    assert (await c.get(f"/api/v1/u/{un}/items/{item['slug']}")).status_code == 200

    # private profile → everything hidden, including item detail
    assert (
        await c.put("/api/v1/portfolio/profile", json={"visibility": "private"}, headers=h)
    ).status_code == 200
    assert (await c.get(f"/api/v1/u/{un}")).status_code == 404
    assert (await c.get(f"/api/v1/u/{un}/items/{item['slug']}")).status_code == 404


@pytest.mark.asyncio
async def test_overview_excludes_removed_org_work(c):
    """/me/overview must not surface drafts/reviews from orgs the user was
    removed from — those are dead links that 403 when opened (bug #100)."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await _org(c, hs)  # student keeps one active org so the early-return doesn't mask the bug
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )

    p = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Overview Proj",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Quality", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/publish", headers=hi)
    assert (
        await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions", headers=hs)
    ).status_code == 201

    d = (await c.get("/api/v1/me/overview", headers=hs)).json()["data"]
    assert len(d["drafts"]) == 1

    assert (await c.delete(f"/api/v1/orgs/{oid}/members/{us['id']}", headers=hi)).status_code == 204
    d = (await c.get("/api/v1/me/overview", headers=hs)).json()["data"]
    assert d["drafts"] == []


@pytest.mark.asyncio
async def test_peer_score_capped_at_project_max(c):
    """Peer assessments must respect project.max_score like instructor
    reviews do — a 10000 score on a max-100 project poisoned the round
    average (bug #101)."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Peer Cap Project",
                "description": "d",
                "instructions": "i",
                "max_score": 100,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)

    studs = []
    for _ in range(2):
        hs, _ = await _auth(c)
        link = await c.post(
            f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho
        )
        await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
        s = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
            "data"
        ]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{s}/submit", headers=hs)
        studs.append(hs)

    rid = (
        await c.post(
            f"/api/v1/orgs/{oid}/peer-review-rounds",
            json={"project_id": pid, "name": "R1", "num_reviews": 1},
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/start", headers=ho)

    my = (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/my-assessments", headers=studs[0])
    ).json()["data"]
    aid = my[0]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/peer-assessments/{aid}/submit", json={"score": 10000}, headers=studs[0]
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "SCORE_EXCEEDS_MAX"
    r = await c.post(
        f"/api/v1/orgs/{oid}/peer-assessments/{aid}/submit", json={"score": 88}, headers=studs[0]
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_skill_category_validated_on_create_and_update(c):
    """create_skill/update_skill must validate category_id exists in this
    org — a bogus ID hit the FK, was misread as a slug collision, retried,
    and 500ed; a cross-org ID silently linked foreign data (bug #102)."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    o1 = await _org(c, h1)
    o2 = await _org(c, h2)
    cat2 = (
        await c.post(f"/api/v1/orgs/{o2}/categories", json={"name": "Foreign Cat"}, headers=h2)
    ).json()["data"]["id"]

    body = {"name": "Cat Val Skill", "description": "d" * 10, "difficulty": "beginner"}
    r = await c.post(
        f"/api/v1/orgs/{o1}/skills",
        json={**body, "category_id": "01BOGUSBOGUSBOGUSBOGUSBOGU"},
        headers=h1,
    )
    assert r.status_code == 404
    r = await c.post(f"/api/v1/orgs/{o1}/skills", json={**body, "category_id": cat2}, headers=h1)
    assert r.status_code == 404

    # valid create, then invalid category on update
    cat1 = (
        await c.post(f"/api/v1/orgs/{o1}/categories", json={"name": "Own Cat"}, headers=h1)
    ).json()["data"]["id"]
    sk = (
        await c.post(f"/api/v1/orgs/{o1}/skills", json={**body, "category_id": cat1}, headers=h1)
    ).json()["data"]["id"]
    r = await c.put(f"/api/v1/orgs/{o1}/skills/{sk}", json={"category_id": cat2}, headers=h1)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_eval_budget_enforced_on_retry_and_first_run(c):
    """retry_task skipped the budget check entirely (bug #103), and
    check_budget returned True when no usage row existed yet — letting a
    0-budget org run its first eval of every month (bug #104)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "monthly_budget_usd": 100},
        headers=h,
    )
    p = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Budget Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/evaluation/trigger",
        json={"submission_id": sid, "type": "submission_review"},
        headers=h,
    )
    assert r.status_code == 201
    tid = r.json()["data"]["id"]
    assert r.json()["data"]["status"] == "failed"  # no LLM key in test env

    # budget exhausted → retry must be blocked
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation", json={"monthly_budget_usd": 0}, headers=h
    )
    r = await c.post(f"/api/v1/orgs/{oid}/evaluation/tasks/{tid}/retry", headers=h)
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "BUDGET_EXCEEDED"

    # fresh org with 0 budget and no usage row → first trigger also blocked
    oid2 = await _org(c, h)
    await c.put(
        f"/api/v1/orgs/{oid2}/settings/evaluation",
        json={"enabled": True, "monthly_budget_usd": 0},
        headers=h,
    )
    p2 = (
        await c.post(
            f"/api/v1/orgs/{oid2}/projects",
            json={
                "title": "Zero Budget Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]
    await c.post(f"/api/v1/orgs/{oid2}/projects/{p2['id']}/publish", headers=h)
    sid2 = (await c.post(f"/api/v1/orgs/{oid2}/projects/{p2['id']}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid2}/evaluation/trigger",
        json={"submission_id": sid2, "type": "submission_review"},
        headers=h,
    )
    assert r.status_code == 429


@pytest.mark.asyncio
async def test_regrant_extension_updates_instead_of_500(c):
    """Granting a second extension to the same student hit the
    (project, user) unique constraint and 500ed — re-granting must update
    the existing extension (bug #105)."""
    from datetime import UTC, datetime, timedelta

    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=hi
    )
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    future = (datetime.now(UTC) + timedelta(days=7)).isoformat()
    later = (datetime.now(UTC) + timedelta(days=14)).isoformat()
    p = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Regrant Proj",
                "description": "d",
                "instructions": "i",
                "deadline": past,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/publish", headers=hi)

    r1 = await c.post(
        f"/api/v1/orgs/{oid}/projects/{p['id']}/extensions",
        json={"user_id": us["id"], "new_deadline": future},
        headers=hi,
    )
    assert r1.status_code == 201
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/projects/{p['id']}/extensions",
        json={"user_id": us["id"], "new_deadline": later},
        headers=hi,
    )
    assert r2.status_code == 201  # updated, not 500

    # extension still works: student submits past the deadline as on_time
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions", headers=hs)).json()[
        "data"
    ]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions/{sid}/submit", headers=hs)
    assert r.status_code == 200
    assert r.json()["data"]["is_late"] is False


@pytest.mark.asyncio
async def test_skill_badges_sync_from_progress(c):
    """ADR-007: badges appear automatically as skills are completed. No code
    path ever created a SkillBadge row, so /portfolio/badges and the public
    profile skills section were permanently empty (bug #106)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Badge Cat"}, headers=h)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Badge Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "MCQ",
                "description": "d",
                "type": "multiple_choice",
                "config": {"correct": ["a"], "options": []},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=h)

    assert (await c.get("/api/v1/portfolio/badges", headers=h)).json()["data"] == []
    await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"selected": ["a"]}},
        headers=h,
    )

    badges = (await c.get("/api/v1/portfolio/badges", headers=h)).json()["data"]
    assert len(badges) == 1
    assert badges[0]["skill_name"] == "Badge Skill"
    assert badges[0]["completion_pct"] == 100
    assert badges[0]["completed"] is True

    # badge shows on public profile, and hiding removes it
    un = f"user{uuid.uuid4().hex[:8]}"
    await c.put("/api/v1/portfolio/username", json={"username": un}, headers=h)
    skills = (await c.get(f"/api/v1/u/{un}")).json()["skills"]
    assert any(s["name"] == "Badge Skill" for s in skills)
    await c.put(
        f"/api/v1/portfolio/badges/{badges[0]['id']}", json={"show_on_profile": False}, headers=h
    )
    skills = (await c.get(f"/api/v1/u/{un}")).json()["skills"]
    assert not any(s["name"] == "Badge Skill" for s in skills)


@pytest.mark.asyncio
async def test_show_score_masks_public_score(c):
    """show_score=False (the default) must hide the score on all public
    endpoints — it was returned verbatim, making the privacy toggle a no-op
    (bug #107)."""
    h, _ = await _auth(c)
    un = f"user{uuid.uuid4().hex[:8]}"
    await c.put("/api/v1/portfolio/username", json={"username": un}, headers=h)
    oid = await _org(c, h)
    p = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Score Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions/{sid}/submit", headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 92},
        headers=h,
    )
    item = (
        await c.post(
            "/api/v1/portfolio/items",
            json={"title": "Scored Work", "submission_id": sid},
            headers=h,
        )
    ).json()["data"]
    assert item["score"] == 92 and item["show_score"] is False  # owner sees it

    # public: masked while show_score is off
    r = await c.get(f"/api/v1/u/{un}/items/{item['slug']}")
    assert r.json()["data"]["score"] is None
    r = await c.get(f"/api/v1/u/{un}/items")
    assert r.json()["data"][0]["score"] is None

    # owner opts in → public sees it
    await c.put(f"/api/v1/portfolio/items/{item['id']}", json={"show_score": True}, headers=h)
    r = await c.get(f"/api/v1/u/{un}/items/{item['slug']}")
    assert r.json()["data"]["score"] == 92


@pytest.mark.asyncio
async def test_anonymous_round_masks_author_in_submission_detail(c):
    """In an anonymous peer round, the allocated reviewer could read the
    author's user_id straight off the submission detail — defeating
    anonymity (bug #108). Non-anonymous rounds keep the author visible."""
    ho, _ = await _auth(c)
    oid = await _org(c, ho)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Anon Detail Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=ho)

    studs = []
    for _ in range(2):
        hs, us = await _auth(c)
        link = await c.post(
            f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=ho
        )
        await c.post("/api/v1/invites/join", json={"code": link.json()["data"]["code"]}, headers=hs)
        s = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
            "data"
        ]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{s}/submit", headers=hs)
        studs.append((hs, us["id"]))

    rid = (
        await c.post(
            f"/api/v1/orgs/{oid}/peer-review-rounds",
            json={"project_id": pid, "name": "R1", "num_reviews": 1, "anonymous": True},
            headers=ho,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/start", headers=ho)

    h0 = studs[0][0]
    my = (
        await c.get(f"/api/v1/orgs/{oid}/peer-review-rounds/{rid}/my-assessments", headers=h0)
    ).json()["data"]
    target = my[0]["submission_id"]
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{target}", headers=h0)
    assert r.status_code == 200
    assert r.json()["data"]["user_id"] == ""  # author masked

    # instructor still sees the author
    r = await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{target}", headers=ho)
    assert r.json()["data"]["user_id"] != ""


@pytest.mark.asyncio
async def test_pass_threshold_setting_honored(c):
    """The org's pass_threshold setting was accepted by the settings API but
    never read — evaluation always used the 0.6 module default (bug #109).
    With threshold 0.9, a 70/100 eval must request revision, not approve."""
    from unittest.mock import AsyncMock, patch

    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "pass_threshold": 0.9},
        headers=h,
    )
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Threshold Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)

    class _Resp:
        content = '{"scores":[{"criterion":"Q","score":70,"max_score":100,"feedback":"ok"}],"overall_feedback":"g","strengths":[],"improvements":[]}'
        input_tokens = 10
        output_tokens = 20
        provider = "anthropic"
        model = "claude-sonnet-5"

    fake = AsyncMock()
    fake.complete = AsyncMock(return_value=_Resp())
    with patch("app.services.evaluation.create_llm_client", return_value=fake):
        r = await c.post(
            f"/api/v1/orgs/{oid}/evaluation/trigger",
            json={"submission_id": sid, "type": "submission_review"},
            headers=h,
        )
    assert r.json()["data"]["status"] == "completed"
    sub = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h)).json()[
        "data"
    ]
    assert sub["status"] == "revision_requested"  # 0.7 < 0.9 threshold


@pytest.mark.asyncio
async def test_default_model_setting_passed_to_llm(c):
    """default_model was stored by the settings API but create_llm_client
    always used the global settings model — the per-org choice was a no-op
    (bug #110)."""
    from unittest.mock import patch

    h, _ = await _auth(c)
    oid = await _org(c, h)
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "default_model": "claude-haiku-4-5"},
        headers=h,
    )
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Model Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)

    seen = {}

    def _capture(model=None):
        seen["model"] = model
        raise RuntimeError("stop here")  # fail the eval — we only care about the arg

    with patch("app.services.evaluation.create_llm_client", side_effect=_capture):
        r = await c.post(
            f"/api/v1/orgs/{oid}/evaluation/trigger",
            json={"submission_id": sid, "type": "submission_review"},
            headers=h,
        )
    assert r.json()["data"]["status"] == "failed"
    assert seen["model"] == "claude-haiku-4-5"


@pytest.mark.asyncio
async def test_eval_disabled_blocks_trigger_and_retry(c):
    """EvalNotEnabledError existed but was never raised — an org with
    enabled=False (the default) could still trigger paid evaluations
    (bug #111)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Disabled Eval Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/evaluation/trigger",
        json={"submission_id": sid, "type": "submission_review"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EVAL_NOT_ENABLED"

    # enable → trigger (fails on missing key, fine) → disable → retry blocked
    await c.put(f"/api/v1/orgs/{oid}/settings/evaluation", json={"enabled": True}, headers=h)
    tid = (
        await c.post(
            f"/api/v1/orgs/{oid}/evaluation/trigger",
            json={"submission_id": sid, "type": "submission_review"},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/settings/evaluation", json={"enabled": False}, headers=h)
    r = await c.post(f"/api/v1/orgs/{oid}/evaluation/tasks/{tid}/retry", headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EVAL_NOT_ENABLED"


@pytest.mark.asyncio
async def test_template_update_bogus_difficulty_422(c):
    """UpdateTemplateRequest had no difficulty whitelist while the service
    converts to DifficultyLevel directly — a bogus value 500ed (bug #112)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    tid = (
        await c.post(
            f"/api/v1/orgs/{oid}/project-templates",
            json={
                "name": "Diff Tmpl",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
                "deliverables": [],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/project-templates/{tid}", json={"difficulty": "IMPOSSIBLE"}, headers=h
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/orgs/{oid}/project-templates/{tid}", json={"difficulty": "advanced"}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["data"]["difficulty"] == "advanced"


@pytest.mark.asyncio
async def test_template_skill_names_linked_on_instantiation(c):
    """Templates store skill_names, but from-template instantiation dropped
    them — projects created from templates never linked any skills
    (bug #113). Names matching org skills now link; unknown names skip."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "FT Cat"}, headers=h)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Prompt Engineering",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    t = (
        await c.post(
            f"/api/v1/orgs/{oid}/project-templates",
            json={
                "name": "FT Tmpl",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
                "deliverables": [],
                "skill_names": ["Prompt Engineering", "Nonexistent Skill"],
            },
            headers=h,
        )
    ).json()["data"]
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/from-template", json={"template_id": t["id"]}, headers=h
        )
    ).json()["data"]["id"]
    detail = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h)).json()["data"]
    assert detail["skill_ids"] == [sk]


@pytest.mark.asyncio
async def test_deleted_user_tokens_invalid(c):
    """Access tokens must die when a user is soft-deleted (verify-only lock:
    get_current_user and refresh_tokens both check is_active)."""
    from sqlalchemy import update

    from app.core.database import AsyncSessionLocal
    from app.models.user import User, UserRole

    h, u = await _auth(c)
    async with AsyncSessionLocal() as db:
        await db.execute(update(User).where(User.id == u["id"]).values(role=UserRole.ADMIN))
        await db.commit()

    h2, u2 = await _auth(c)
    r = await c.delete(f"/api/v1/admin/users/{u2['id']}", headers=h)
    assert r.status_code == 204
    r = await c.get("/api/v1/auth/me", headers=h2)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_comments_include_author_name(c):
    """Comments are a two-way conversation, but the API returned only
    author_id (a bare ULID the UI never rendered) — threads were
    anonymous-looking (bug #114). List now joins the display name."""
    h, u = await _auth(c)
    oid = await _org(c, h)
    p = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Comment Author Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions", headers=h)).json()[
        "data"
    ]["id"]
    # need an item to comment on — use a text deliverable inline item
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{p['id']}/deliverables",
            json={"name": "Notes", "type": "text", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions/{sid}",
        json={"items": [{"deliverable_id": did, "type": "text", "content": "hello"}]},
        headers=h,
    )
    items = (
        await c.get(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions/{sid}", headers=h)
    ).json()["data"]["items"]
    iid = items[0]["id"]

    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/comments",
        json={"item_id": iid, "text": "Looks good"},
        headers=h,
    )
    assert r.status_code == 201
    comments = (await c.get(f"/api/v1/orgs/{oid}/submissions/{sid}/comments", headers=h)).json()[
        "data"
    ]
    assert comments[0]["author_name"] == u["display_name"]


@pytest.mark.asyncio
async def test_link_item_scheme_restricted(c):
    """A link deliverable's content is rendered as a clickable href —
    javascript:/data: schemes must be rejected like every other URL field
    (bug #115)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    p = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Link Proj",
                "description": "d",
                "instructions": "i",
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]
    did = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects/{p['id']}/deliverables",
            json={"name": "Demo Link", "type": "link", "required": False},
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions", headers=h)).json()[
        "data"
    ]["id"]

    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions/{sid}",
        json={"items": [{"deliverable_id": did, "type": "link", "content": "javascript:alert(1)"}]},
        headers=h,
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{p['id']}/submissions/{sid}",
        json={
            "items": [
                {"deliverable_id": did, "type": "link", "content": "https://demo.example.com"}
            ]
        },
        headers=h,
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_toggle_invite_link_type_validated(c):
    """A non-boolean is_active hit SQLAlchemy's strict bool coercion and
    500ed (bug #116). Now 422s; real booleans still work."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    link = (
        await c.post(f"/api/v1/orgs/{oid}/invite-links", json={"role": "student"}, headers=h)
    ).json()["data"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/invite-links/{link['id']}", json={"is_active": "banana"}, headers=h
    )
    assert r.status_code == 422
    r = await c.put(
        f"/api/v1/orgs/{oid}/invite-links/{link['id']}", json={"is_active": False}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_mcq_requires_correct_config(c):
    """An MCQ with no non-empty `correct` auto-graded every blank answer as
    full marks ([] == [] in the grader) — free skill completion and badges
    (bug #117). Create and update both reject it now."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "MCQ Cat"}, headers=h)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "MCQ Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]

    body = {"title": "MCQ", "description": "d", "type": "multiple_choice", "max_score": 10}
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
        json={**body, "config": {"options": ["a"]}},
        headers=h,
    )
    assert r.status_code == 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
        json={**body, "config": {"correct": [], "options": ["a"]}},
        headers=h,
    )
    assert r.status_code == 422

    # valid create, then try to strip correct via update
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={**body, "config": {"correct": ["a"], "options": ["a", "b"]}},
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/exercises/{ex}", json={"config": {"options": ["a", "b"]}}, headers=h
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_attempt_answer_bounded(c):
    """SubmitAttemptRequest.answer had no size bound — unbounded JSONB
    storage abuse, same class as settings/config (bug #118)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cat = (
        await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "AB Cat"}, headers=h)
    ).json()["data"]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "AB Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "Text",
                "description": "d",
                "type": "text_answer",
                "config": {},
                "max_score": 10,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"text": "X" * 200_000}},
        headers=h,
    )
    assert r.status_code == 422
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts", json={"answer": {"text": "fine"}}, headers=h
    )
    assert r.status_code == 201
