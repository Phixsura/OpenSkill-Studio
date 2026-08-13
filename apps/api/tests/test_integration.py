"""Integration tests with real PostgreSQL + Redis.

Run with: cd apps/api && APP_ENV=test PYTHONPATH=. uv run pytest tests/test_integration.py -v
Requires: make infra-up && PYTHONPATH=. uv run alembic upgrade head
"""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@integration.com"


@pytest_asyncio.fixture
async def client():
    from contextlib import asynccontextmanager

    from app.core.database import engine
    from app.main import app

    @asynccontextmanager
    async def _noop_lifespan(a):
        yield

    original = app.router.lifespan_context
    app.router.lifespan_context = _noop_lifespan
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = original
    await engine.dispose()


async def _register(cl):
    email = _unique_email()
    r = await cl.post("/api/v1/auth/register", json={
        "email": email, "password": "TestPass123!", "display_name": "IntTest",
    })
    assert r.status_code == 201, f"Register failed ({r.status_code}): {r.text}"
    data = r.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return headers, data["user"]


# ── Auth ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_creates_user(client):
    r = await client.post("/api/v1/auth/register", json={
        "email": _unique_email(), "password": "Valid123!", "display_name": "New User",
    })
    assert r.status_code == 201
    assert r.json()["user"]["role"] == "student"


@pytest.mark.asyncio
async def test_login_success(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "TestPass123!", "display_name": "Login",
    })
    r = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "TestPass123!",
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "TestPass123!", "display_name": "WP",
    })
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": "Wrong123!"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_register_duplicate(client):
    email = _unique_email()
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Valid123!", "display_name": "First",
    })
    r = await client.post("/api/v1/auth/register", json={
        "email": email, "password": "Valid123!", "display_name": "Second",
    })
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_get_and_update_me(client):
    headers, user = await _register(client)
    r = await client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["data"]["email"] == user["email"]

    r2 = await client.put("/api/v1/auth/me", json={"display_name": "Updated"}, headers=headers)
    assert r2.status_code == 200
    assert r2.json()["data"]["display_name"] == "Updated"


# ── Health ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_ready(client):
    r = await client.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert r.json()["components"]["database"] == "ok"


# ── Full flow ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_org_skill_project_portfolio_flow(client):
    headers, _ = await _register(client)

    # Org
    r = await client.post("/api/v1/orgs", json={"name": f"Org-{uuid.uuid4().hex[:6]}"}, headers=headers)
    assert r.status_code == 201
    org_id = r.json()["data"]["id"]

    # Category + Skill + Exercise
    r2 = await client.post(f"/api/v1/orgs/{org_id}/categories", json={"name": "AI"}, headers=headers)
    cat_id = r2.json()["data"]["id"]

    r3 = await client.post(f"/api/v1/orgs/{org_id}/skills", json={
        "category_id": cat_id, "name": "Prompting", "description": "Learn",
    }, headers=headers)
    skill_id = r3.json()["data"]["id"]

    r4 = await client.post(f"/api/v1/orgs/{org_id}/skills/{skill_id}/exercises", json={
        "title": "MCQ", "description": "Pick", "type": "multiple_choice",
        "config": {"correct": ["a"], "options": [{"id": "a", "text": "Right"}]},
    }, headers=headers)
    ex_id = r4.json()["data"]["id"]

    # Attempt
    r5 = await client.post(f"/api/v1/orgs/{org_id}/exercises/{ex_id}/attempts", json={
        "answer": {"selected": ["a"]},
    }, headers=headers)
    assert r5.json()["data"]["is_correct"] is True

    # Project + Submission + Review
    r6 = await client.post(f"/api/v1/orgs/{org_id}/projects", json={
        "title": "Chatbot", "description": "Build", "instructions": "Go",
        "rubric": [{"criterion": "Q", "max_score": 100}],
    }, headers=headers)
    proj_id = r6.json()["data"]["id"]

    r7 = await client.post(f"/api/v1/orgs/{org_id}/projects/{proj_id}/submissions", headers=headers)
    sub_id = r7.json()["data"]["id"]
    await client.post(f"/api/v1/orgs/{org_id}/projects/{proj_id}/submissions/{sub_id}/submit", headers=headers)

    r8 = await client.post(f"/api/v1/orgs/{org_id}/submissions/{sub_id}/reviews", json={
        "status": "approved", "score": 95, "feedback": "Great!",
    }, headers=headers)
    assert r8.status_code == 201

    # Portfolio
    r9 = await client.get("/api/v1/portfolio/profile", headers=headers)
    assert r9.status_code == 200

    r10 = await client.post("/api/v1/portfolio/items", json={
        "title": "My Project", "tags": ["ai"],
    }, headers=headers)
    assert r10.status_code == 201
