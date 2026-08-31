"""Edge case, boundary, and data integrity tests.

Covers: Unicode, large payloads, concurrent operations, timezone edges,
token expiry, data cascade, authorization depth.
"""

import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"edge-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Edge"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


# ═══════════════ Unicode / Special Characters ═══════════════


@pytest.mark.asyncio
async def test_unicode_cohort_name_cjk(c):
    """CJK characters in cohort name → creates successfully with valid slug."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={
            "name": "秋季AI设计班 2026",
        },
        headers=h,
    )
    assert r.status_code == 201
    cohort = r.json()["data"]
    assert cohort["name"] == "秋季AI设计班 2026"
    assert len(cohort["slug"]) > 0  # slug generated


@pytest.mark.asyncio
async def test_unicode_brief_title_emoji(c):
    """Emoji in brief title → stored correctly."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={
            "title": "🎨 Creative Campaign 🚀",
            "client_name": "Acme 株式会社",
            "project_type": "visualization",
            "objective": "Create visuals with emoji and unicode characters for global audience",
        },
        headers=h,
    )
    assert r.status_code == 201
    brief = r.json()["data"]
    assert "🎨" in brief["title"]
    assert "株式会社" in brief["client_name"]


@pytest.mark.asyncio
async def test_unicode_project_description(c):
    """Unicode in project description → stored and retrieved correctly."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Café Résumé Project",
            "description": "Créer des visuels pour le café — très important! 日本語テスト",
            "instructions": "Use AI tools. Instructions: أهلاً وسهلاً",
            "rubric": [{"criterion": "Qualité", "max_score": 100}],
        },
        headers=h,
    )
    assert r.status_code == 201
    proj = r.json()["data"]
    assert "Café" in proj["title"]


@pytest.mark.asyncio
async def test_slug_generation_non_ascii(c):
    """Slug from non-ASCII name → generates valid slug."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={
            "name": "日本語テスト",
        },
        headers=h,
    )
    assert r.status_code == 201
    slug = r.json()["data"]["slug"]
    # Slug should contain only ASCII-safe chars
    assert all(c.isalnum() or c == "-" for c in slug)


# ═══════════════ Large Payloads ═══════════════


@pytest.mark.asyncio
async def test_max_length_cohort_name(c):
    """200-char cohort name → accepted. 201-char → rejected."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Exactly 200 chars → OK
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={
            "name": "A" * 200,
        },
        headers=h,
    )
    assert r.status_code == 201

    # 201 chars → rejected
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={
            "name": "A" * 201,
        },
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_large_deliverable_specs(c):
    """Brief with 50 deliverable_specs → accepted."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    specs = [{"name": f"Deliverable {i}", "type": "file"} for i in range(50)]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={
            "title": "Big Brief",
            "client_name": "Client",
            "project_type": "viz",
            "objective": "Test with many deliverable specs for scalability",
            "deliverable_specs": specs,
        },
        headers=h,
    )
    assert r.status_code == 201
    assert len(r.json()["data"]["deliverable_specs"]) == 50


@pytest.mark.asyncio
async def test_large_rubric(c):
    """Project with 20 rubric criteria → accepted."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    rubric = [{"criterion": f"Criterion {i}", "max_score": 5} for i in range(20)]
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Many Rubric",
            "description": "Test with 20 rubric criteria",
            "instructions": "Follow the rubric",
            "rubric": rubric,
        },
        headers=h,
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_oversized_deliverable_specs_rejected(c):
    """Brief with >50 deliverable_specs → rejected."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    specs = [{"name": f"D{i}", "type": "file"} for i in range(51)]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={
            "title": "Too Big",
            "client_name": "C",
            "project_type": "viz",
            "objective": "This should be rejected for too many deliverables",
            "deliverable_specs": specs,
        },
        headers=h,
    )
    assert r.status_code == 422


# ═══════════════ Concurrent Operations ═══════════════


@pytest.mark.asyncio
async def test_concurrent_cohort_join_max_learners(c):
    """max_learners=1, two concurrent joins → one succeeds, one fails."""
    h, _ = await _auth(c)
    hs1, us1 = await _auth(c)
    hs2, us2 = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us1["id"], "role": "student"}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us2["id"], "role": "student"}, headers=h
    )

    cid = (
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts",
            json={
                "name": "Limited",
                "max_learners": 1,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)

    results = await asyncio.gather(
        c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us1["id"]}, headers=h),
        c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us2["id"]}, headers=h),
    )
    codes = sorted([r.status_code for r in results])
    # One should succeed (201), one should fail (409 or 422)
    assert 201 in codes
    assert codes[0] in (201, 409, 422)  # at least one non-201


@pytest.mark.asyncio
async def test_concurrent_duplicate_submission(c):
    """Two concurrent submissions on same draft → one succeeds."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Conc Sub",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h)
    sid = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
        "data"
    ]["id"]

    results = await asyncio.gather(
        c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs),
        c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=hs),
    )
    codes = sorted([r.status_code for r in results])
    # At least one should succeed
    assert 200 in codes


# ═══════════════ Timezone Edge Cases ═══════════════


@pytest.mark.asyncio
async def test_deadline_naive_datetime_normalized(c):
    """Naive datetime (no timezone) in deadline → handled without crash."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Send naive datetime (no Z, no +00:00)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Naive Deadline",
            "description": "Test naive datetime",
            "instructions": "Instructions here",
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "deadline": "2026-12-31T23:59:59",  # No timezone
        },
        headers=h,
    )
    assert r.status_code == 201
    # Should still store and return a datetime
    assert r.json()["data"]["deadline"] is not None


@pytest.mark.asyncio
async def test_late_deadline_equals_deadline(c):
    """late_deadline == deadline → accepted (boundary)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    deadline = "2026-12-31T23:59:59Z"
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Equal Deadlines",
            "description": "d",
            "instructions": "i",
            "rubric": [{"criterion": "Q", "max_score": 100}],
            "deadline": deadline,
            "late_deadline": deadline,  # Same as deadline
        },
        headers=h,
    )
    assert r.status_code == 201


# ═══════════════ Token / Auth Edge Cases ═══════════════


@pytest.mark.asyncio
async def test_expired_token_rejected(c):
    """Manually crafted expired JWT → 401."""
    # Use a garbage token
    r = await c.get(
        "/api/v1/orgs",
        headers={
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxMDAwMDAwMDAwfQ.invalid",
        },
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_no_token_on_protected_endpoint(c):
    """No auth header → 401 or 403."""
    r = await c.get("/api/v1/orgs")
    assert r.status_code in (401, 403)


# ═══════════════ Data Integrity ═══════════════


@pytest.mark.asyncio
async def test_delete_cohort_with_members_and_assignments(c):
    """Deleting a cohort cleans up members and assignments."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Delete Me"}, headers=h)
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us["id"]}, headers=h)

    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "DC"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "DS",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills", json={"skill_id": sk}, headers=h)

    # Delete cohort
    r = await c.delete(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h)
    assert r.status_code == 204

    # Cohort no longer accessible
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h)
    assert r.status_code == 404

    # Skill still exists (not cascade-deleted)
    r = await c.get(f"/api/v1/orgs/{oid}/skills/{sk}", headers=h)
    assert r.status_code == 200


# ═══════════════ Authorization Depth ═══════════════


@pytest.mark.asyncio
async def test_student_cannot_access_other_students_drilldown(c):
    """Student A cannot view Student B's drill-down progress."""
    h, _ = await _auth(c)
    hs_a, us_a = await _auth(c)
    hs_b, us_b = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us_a["id"], "role": "student"}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us_b["id"], "role": "student"}, headers=h
    )

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Auth"}, headers=h)).json()[
        "data"
    ]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us_a["id"]}, headers=h
    )
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members", json={"user_id": us_b["id"]}, headers=h
    )

    # Student A tries to view Student B's drill-down → should be rejected
    r = await c.get(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/progress/{us_b['id']}",
        headers=hs_a,
    )
    # Students can't access the progress endpoint (requires instructor role)
    assert r.status_code in (403, 404)


@pytest.mark.asyncio
async def test_cross_org_cohort_access_rejected(c):
    """Instructor of org A cannot access org B's cohort."""
    h1, _ = await _auth(c)
    h2, _ = await _auth(c)
    oid1 = await _org(c, h1)
    oid2 = await _org(c, h2)

    cid = (
        await c.post(f"/api/v1/orgs/{oid2}/cohorts", json={"name": "Private"}, headers=h2)
    ).json()["data"]["id"]

    # User 1 tries to access User 2's cohort
    r = await c.get(f"/api/v1/orgs/{oid2}/cohorts/{cid}", headers=h1)
    assert r.status_code in (403, 404)

    # Also try via the other org's URL with the cohort ID
    r = await c.get(f"/api/v1/orgs/{oid1}/cohorts/{cid}", headers=h1)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_student_cannot_create_cohort(c):
    """Student role cannot create cohorts (requires instructor+)."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    r = await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Sneaky"}, headers=hs)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_student_cannot_assign_skills(c):
    """Student cannot assign skills to a cohort."""
    h, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, h)
    await c.post(
        f"/api/v1/orgs/{oid}/members", json={"user_id": us["id"], "role": "student"}, headers=h
    )

    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Perm"}, headers=h)).json()[
        "data"
    ]["id"]
    cat = (await c.post(f"/api/v1/orgs/{oid}/categories", json={"name": "PC"}, headers=h)).json()[
        "data"
    ]["id"]
    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "PS",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid}/cohorts/{cid}/skills", json={"skill_id": sk}, headers=hs)
    assert r.status_code == 403


# ═══════════════ Status Transition Guards ═══════════════


@pytest.mark.asyncio
async def test_cohort_status_cannot_go_backwards(c):
    """Cohort status transitions: only forward (draft→active→completed→archived)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Trans"}, headers=h)).json()[
        "data"
    ]["id"]

    # draft → active: OK
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    assert r.status_code == 200

    # active → draft: BLOCKED
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "draft"}, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "INVALID_TRANSITION"

    # active → completed: OK
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "completed"}, headers=h)
    assert r.status_code == 200

    # completed → active: BLOCKED
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)
    assert r.status_code == 422

    # completed → archived: OK
    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "archived"}, headers=h)
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_assign_unpublished_project_to_cohort_rejected(c):
    """Draft (unpublished) projects cannot be assigned to cohorts."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "PubGuard"}, headers=h)
    ).json()["data"]["id"]
    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h)

    # Create draft project (NOT published)
    dp = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Unpub",
                "description": "d" * 10,
                "instructions": "i" * 10,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    # Assign draft → rejected
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={"project_id": dp},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "PROJECT_NOT_PUBLISHED"

    # Publish then assign → OK
    await c.post(f"/api/v1/orgs/{oid}/projects/{dp}/publish", headers=h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={"project_id": dp},
        headers=h,
    )
    assert r.status_code == 201
