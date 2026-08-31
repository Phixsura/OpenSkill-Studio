"""End-to-end test: full operational loop from cohort → brief → submission → eval → review."""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"e2e-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "E2E"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_full_cohort_to_eval_lifecycle(c):
    """Complete operational loop:
    1. Admin creates org + cohort
    2. Enrolls instructor + learners
    3. Creates client brief
    4. Converts brief to commercial AI visual project
    5. Assigns project to cohort with deadline override
    6. Learner submits text (image eval requires S3)
    7. Multimodal eval triggered (mock LLM)
    8. Instructor reviews with manual override
    9. Cohort dashboard reflects correct progress
    10. Student in different cohort cannot see the project
    """
    # 1. Create org + users
    h_admin, _ = await _auth(c)
    h_instructor, u_instructor = await _auth(c)
    h_learner_a, u_learner_a = await _auth(c)
    h_learner_b, u_learner_b = await _auth(c)

    oid = await _org(c, h_admin)
    for u, role in [
        (u_instructor, "instructor"),
        (u_learner_a, "student"),
        (u_learner_b, "student"),
    ]:
        await c.post(
            f"/api/v1/orgs/{oid}/members",
            json={"user_id": u["id"], "role": role},
            headers=h_admin,
        )

    # 2. Create cohort + enroll members
    cohort = (
        await c.post(
            f"/api/v1/orgs/{oid}/cohorts",
            json={"name": "AI Commerce — Fall 2026", "description": "First commercial cohort"},
            headers=h_admin,
        )
    ).json()["data"]
    cid = cohort["id"]
    assert cohort["status"] == "draft"

    await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h_admin)

    # Enroll instructor and learner A (learner B stays out)
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u_instructor["id"], "role": "instructor"},
        headers=h_admin,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u_learner_a["id"], "role": "learner"},
        headers=h_admin,
    )

    # 3. Create client brief
    brief = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": "Acme Q4 Product Campaign",
                "client_name": "Acme Corp",
                "project_type": "product_visualization",
                "objective": "Create hero images and a 15s video for Q4 product launch",
                "target_audience": "Young professionals 25-35",
                "tone_and_style": "Modern, clean, premium",
                "deliverable_specs": [
                    {
                        "name": "Hero Image",
                        "type": "image",
                        "description": "Main product shot",
                        "required": False,
                    },
                    {"name": "Campaign Text", "type": "text", "description": "Tagline + copy"},
                ],
            },
            headers=h_instructor,
        )
    ).json()["data"]
    bid = brief["id"]
    assert brief["status"] == "draft"

    # 4. Convert brief to project
    project = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
            json={
                "rubric": [
                    {"criterion": "Brief Alignment", "max_score": 40},
                    {"criterion": "Visual Quality", "max_score": 35},
                    {"criterion": "Commercial Readiness", "max_score": 25},
                ],
                "cohort_id": cid,
                "deadline": "2030-12-01T00:00:00Z",
            },
            headers=h_instructor,
        )
    ).json()["data"]
    pid = project["id"]
    assert project["project_type"] == "ai_visual"

    # Publish the project
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h_instructor)

    # 5. Assign project to cohort with deadline override
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={
            "project_id": pid,
            "deadline_override": "2030-11-15T00:00:00Z",
            "max_submissions_override": 3,
        },
        headers=h_instructor,
    )

    # 6. Learner A submits
    sub = (
        await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h_learner_a)
    ).json()["data"]
    sid = sub["id"]

    # Add text content to the Campaign Text deliverable
    details = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h_learner_a)).json()[
        "data"
    ]
    text_del = next((d for d in details["deliverables"] if d["name"] == "Campaign Text"), None)
    if text_del:
        await c.put(
            f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
            json={
                "items": [
                    {
                        "deliverable_id": text_del["id"],
                        "type": "text",
                        "content": "Acme Q4: Innovation Meets Design",
                    }
                ]
            },
            headers=h_learner_a,
        )

    r = await c.post(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h_learner_a
    )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"

    # 7. Enable eval + trigger (mock LLM)
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "monthly_budget_usd": 100},
        headers=h_admin,
    )

    class _MockResp:
        content = '{"scores":[{"criterion":"Brief Alignment","score":35,"max_score":40,"feedback":"Good alignment"},{"criterion":"Visual Quality","score":28,"max_score":35,"feedback":"Decent"},{"criterion":"Commercial Readiness","score":20,"max_score":25,"feedback":"Needs polish"}],"overall_feedback":"Solid work","strengths":["alignment"],"improvements":["polish"]}'
        input_tokens = 500
        output_tokens = 200
        provider = "anthropic"
        model = "claude-sonnet-5"

    fake = AsyncMock()
    fake.complete = AsyncMock(return_value=_MockResp())
    with patch("app.services.evaluation.create_llm_client", return_value=fake):
        eval_r = await c.post(
            f"/api/v1/orgs/{oid}/evaluation/trigger",
            json={"submission_id": sid, "type": "submission_review"},
            headers=h_instructor,
        )
    assert eval_r.status_code == 201
    eval_task = eval_r.json()["data"]
    assert eval_task["status"] == "completed"

    # Submission should now have an AI review
    sub_detail = (
        await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h_instructor)
    ).json()["data"]
    assert len(sub_detail["reviews"]) >= 1
    ai_review = sub_detail["reviews"][0]
    assert ai_review["reviewer_type"] == "ai"
    assert ai_review["score"] == 83  # 35+28+20

    # 8. Instructor overrides with manual review
    review_r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={"status": "approved", "score": 90, "feedback": "Excellent commercial work"},
        headers=h_instructor,
    )
    assert review_r.status_code == 201

    # Verify final score reflects instructor review
    sub_final = (
        await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h_instructor)
    ).json()["data"]
    assert sub_final["status"] == "approved"
    assert sub_final["final_score"] == 90  # instructor override, not AI's 83

    # 9. Cohort dashboard reflects progress
    progress = (
        await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=h_instructor)
    ).json()["data"]
    assert progress["total_learners"] == 1
    assert len(progress["projects"]) >= 1
    proj_prog = progress["projects"][0]
    assert proj_prog["approved"] == 1

    # 10. Learner B (not in cohort) cannot see the cohort's project
    r = await c.get(f"/api/v1/orgs/{oid}/projects", headers=h_learner_b)
    assert "Acme Q4 Product Campaign" not in {p["title"] for p in r.json()["data"]}
    # The project was created with cohort_id set, so it's cohort-scoped
    # Learner B is not in the cohort, so they shouldn't see it
    # (unless it's also org-wide — our convert sets cohort_id on the project)


@pytest.mark.asyncio
async def test_application_workflow(c):
    """Learner applies to a brief, instructor accepts."""
    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": us["id"], "role": "student"},
        headers=hi,
    )
    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": "App Brief",
                "client_name": "Client",
                "project_type": "viz",
                "objective": "Make visuals" * 3,
            },
            headers=hi,
        )
    ).json()["data"]["id"]

    # Set brief to open so learner can apply
    await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "open"}, headers=hi)

    # Learner applies
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/apply",
        json={"note": "I have relevant experience"},
        headers=hs,
    )
    assert r.status_code == 201
    app_id = r.json()["data"]["id"]

    # Duplicate application rejected
    r = await c.post(f"/api/v1/orgs/{oid}/briefs/{bid}/apply", json={}, headers=hs)
    assert r.status_code == 409

    # Instructor lists applications
    r = await c.get(f"/api/v1/orgs/{oid}/briefs/{bid}/applications", headers=hi)
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1
    assert r.json()["data"][0]["note"] == "I have relevant experience"

    # Instructor accepts
    r = await c.put(
        f"/api/v1/orgs/{oid}/briefs/{bid}/applications/{app_id}",
        json={"status": "accepted"},
        headers=hi,
    )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "accepted"

    # Student listing applications sees ONLY their own (the brief detail
    # page uses this for the "you have applied" state) — never other
    # members' applications
    r = await c.get(f"/api/v1/orgs/{oid}/briefs/{bid}/applications", headers=hs)
    assert r.status_code == 200
    rows = r.json()["data"]
    assert len(rows) == 1
    assert rows[0]["note"] == "I have relevant experience"


@pytest.mark.asyncio
async def test_cohort_deadline_override_in_submission(c):
    """A cohort's deadline override takes precedence over the project's deadline."""
    from datetime import UTC, datetime, timedelta

    hi, _ = await _auth(c)
    hs, us = await _auth(c)
    oid = await _org(c, hi)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": us["id"], "role": "student"},
        headers=hi,
    )

    # Project with a past deadline
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    future = (datetime.now(UTC) + timedelta(days=7)).isoformat()
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/projects",
            json={
                "title": "Deadline Override Proj",
                "description": "d",
                "instructions": "i",
                "deadline": past,
                "rubric": [{"criterion": "Q", "max_score": 100}],
            },
            headers=hi,
        )
    ).json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=hi)

    # Without cohort override: submission should fail (deadline passed)
    sid1 = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
        "data"
    ]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid1}/submit", headers=hs)
    assert r.status_code == 422  # DEADLINE_PASSED

    # Create cohort with future deadline override
    cid = (
        await c.post(f"/api/v1/orgs/{oid}/cohorts", json={"name": "Override Cohort"}, headers=hi)
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": us["id"]},
        headers=hi,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={"project_id": pid, "deadline_override": future},
        headers=hi,
    )

    # Now the cohort override should let the submission through
    sid2 = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=hs)).json()[
        "data"
    ]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid2}/submit", headers=hs)
    assert r.status_code == 200  # on_time thanks to cohort override
    assert r.json()["data"]["is_late"] is False
