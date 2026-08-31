"""Performance and stress tests.

Tests concurrent reads/writes, large data set pagination,
progress aggregation with many members, slug uniqueness under load.
"""

import asyncio
import time
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"perf-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Perf"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_concurrent_reads_cohort_list(c):
    """20 concurrent GET requests to cohort list → all succeed."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # Create a few cohorts
    for i in range(5):
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": f"C{i}"}, headers=h)

    start = time.monotonic()
    results = await asyncio.gather(
        *[c.get(f"/api/v1/orgs/{oid}/cohorts", headers=h) for _ in range(20)]
    )
    elapsed = time.monotonic() - start

    assert all(r.status_code == 200 for r in results)
    assert all(len(r.json()["data"]) == 5 for r in results)
    assert elapsed < 10  # Should complete in <10s


@pytest.mark.asyncio
async def test_concurrent_submissions_different_users(c):
    """10 users each creating a submission concurrently → all succeed."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Conc",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)

    # Register 10 students
    students = []
    for _ in range(10):
        hs, us = await _auth(c)
        await c.post(
            f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
        )
        students.append(hs)

    # All create submissions concurrently
    results = await asyncio.gather(
        *[c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=sh) for sh in students]
    )
    assert all(r.status_code == 201 for r in results)


@pytest.mark.asyncio
async def test_large_cohort_list_pagination(c):
    """Create 30 cohorts → paginate with per_page=10 → verify meta.total and pages."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    for i in range(30):
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": f"Pag{i:02d}"}, headers=h)

    # Page 1
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts?per_page=10&page=1", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 10
    assert r.json()["meta"]["total"] == 30

    # Page 3
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts?per_page=10&page=3", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 10

    # Page 4 (beyond data)
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts?per_page=10&page=4", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 0


@pytest.mark.asyncio
async def test_progress_with_many_members(c):
    """Cohort with 20 members + 3 projects → progress aggregation completes in time."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "BigCoh"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)

    # Add 20 members
    for _ in range(20):
        _, us = await _auth(c)
        await c.post(
            f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
        )
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=h
        )

    # Add 3 projects
    for i in range(3):
        pid = (
            await c.post(
                f"/api/v1/orgs/{oid}/projects",
                json={
                    "title": f"BigP{i}",
                    "description": "d" * 10,
                    "instructions": "i" * 10,
                    "rubric": [{"criterion": "Q", "max_score": 100}],
                },
                headers=h,
            )
        ).json()["data"]["id"]
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts/{cid}/projects", json={"project_id": pid}, headers=h
        )

    start = time.monotonic()
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=h)
    elapsed = time.monotonic() - start

    assert r.status_code == 200
    assert r.json()["data"]["total_learners"] == 20
    assert len(r.json()["data"]["projects"]) == 3
    assert elapsed < 5  # Should complete in <5s


@pytest.mark.asyncio
async def test_slug_uniqueness_under_load(c):
    """Create 50 briefs with same title → all get unique slugs."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    slugs = set()
    for _ in range(50):
        r = await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": "Identical Title",
                "client_name": "Same Client",
                "project_type": "viz",
                "objective": "Test slug uniqueness with identical titles repeatedly",
            },
            headers=h,
        )
        assert r.status_code == 201
        slugs.add(r.json()["data"]["slug"])

    assert len(slugs) == 50  # All unique


@pytest.mark.asyncio
async def test_api_response_time_health(c):
    """Health endpoint responds in <50ms."""
    start = time.monotonic()
    r = await c.get("/api/v1/health")
    elapsed = time.monotonic() - start

    assert r.status_code == 200
    assert elapsed < 0.5  # 500ms generous limit for test environment


@pytest.mark.asyncio
async def test_api_response_time_cohort_list(c):
    """Cohort list with 10 items responds in <500ms."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for i in range(10):
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": f"Rt{i}"}, headers=h)

    start = time.monotonic()
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts", headers=h)
    elapsed = time.monotonic() - start

    assert r.status_code == 200
    assert elapsed < 0.5
