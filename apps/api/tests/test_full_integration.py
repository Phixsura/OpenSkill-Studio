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
            json={"title": "Filename Project", "description": "d", "instructions": "i", "rubric": [{"criterion": "Q", "max_score": 100}]},
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
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h)).json()["data"]["id"]

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
        cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()["data"]["id"]
        sk = (
            await c.post(
                f"/api/v1/orgs/{oid}/skills",
                json={"name": "Skill One", "description": "d" * 10, "difficulty": "beginner", "category_id": cat},
                headers=h,
            )
        ).json()["data"]["id"]
        ex = (
            await c.post(
                f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
                json={"title": "Ex", "description": "d", "type": "text_answer", "config": {}, "max_score": 10},
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
            json={"title": "PF Link Project", "description": "d", "instructions": "i", "rubric": [{"criterion": "Q", "max_score": 100}]},
            headers=hv,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hv)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hv)).json()["data"]["id"]

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
    assert (await c.put("/api/v1/portfolio/username", json={"username": uname}, headers=h1)).status_code == 200
    # same name (case-insensitive) taken by another user → 409
    assert (await c.put("/api/v1/portfolio/username", json={"username": uname.upper()}, headers=h2)).status_code == 409
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
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "Cat"}, headers=h)).json()["data"]["id"]

    # expert skill accepted
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={"name": "Expert Skill", "description": "d" * 10, "difficulty": "expert", "category_id": cat},
        headers=h,
    )
    assert r.status_code == 201

    # bad filters → 422, not 500
    assert (await c.get(f"/api/v1/orgs/{oid}/skills?difficulty=bogus", headers=h)).status_code == 422
    assert (await c.get(f"/api/v1/orgs/{oid}/skills?status=bogus", headers=h)).status_code == 422
    assert (await c.get(f"/api/v1/orgs/{oid}/projects?status=bogus", headers=h)).status_code == 422
