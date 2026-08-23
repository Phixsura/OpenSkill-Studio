"""Complete end-to-end test: the full operational loop from issue #16.

This is a single large test that exercises every layer of the new system
in sequence, exactly as a real deployment would use it:

  Admin creates org
  → creates cohort
  → enrolls instructor + learners
  → assigns skills (with exercises)
  → creates Client Brief
  → converts brief to commercial AI visual project
  → assigns project to cohort (with deadline override)
  → learner sees project (visibility)
  → other learner does NOT see project (isolation)
  → learner applies to brief (application workflow)
  → instructor accepts application
  → learner submits prompt + text deliverables
  → multimodal AI evaluation runs (mock LLM)
  → instructor sees AI feedback
  → instructor requests revision
  → learner resubmits
  → instructor approves with score override
  → cohort dashboard reflects correct completion
  → learner sees progress in my-dashboard
  → skill progress tracked via badge sync
  → portfolio item publishable from approved submission

Each step's failure pinpoints exactly which link in the chain broke.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"full-{uuid.uuid4().hex[:8]}@test.com"


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


async def _auth(c, name="E2E"):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": name},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    assert r.status_code == 201, f"Org creation failed: {r.json()}"
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_complete_operational_loop(c):
    """The full operational loop from learning → practice → real project →
    evaluation → delivery → capability proof."""

    # ═══════════════════════════════════════════════════════════
    # STEP 1: Organization + Users
    # ═══════════════════════════════════════════════════════════
    h_admin, u_admin = await _auth(c, "Admin Wang")
    h_inst, u_inst = await _auth(c, "Instructor Li")
    h_alice, u_alice = await _auth(c, "Alice Chen")
    h_bob, u_bob = await _auth(c, "Bob Zhang")

    oid = await _org(c, h_admin)

    # Add members
    for u, role in [
        (u_inst, "instructor"),
        (u_alice, "student"),
        (u_bob, "student"),
    ]:
        r = await c.post(
            f"/api/v1/orgs/{oid}/members",
            json={"user_id": u["id"], "role": role},
            headers=h_admin,
        )
        assert r.status_code in (200, 201), f"Add member {u['display_name']}: {r.text[:100]}"

    # ═══════════════════════════════════════════════════════════
    # STEP 2: Create + activate cohort
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts",
        json={
            "name": "AI Visual Commerce — Fall 2026",
            "description": "First commercial AI training cohort",
            "starts_at": "2026-09-01T00:00:00Z",
            "ends_at": "2026-12-31T00:00:00Z",
            "max_learners": 50,
        },
        headers=h_admin,
    )
    assert r.status_code == 201
    cohort = r.json()["data"]
    cid = cohort["id"]
    assert cohort["status"] == "draft"

    r = await c.put(f"/api/v1/orgs/{oid}/cohorts/{cid}", json={"status": "active"}, headers=h_admin)
    assert r.json()["data"]["status"] == "active"

    # ═══════════════════════════════════════════════════════════
    # STEP 3: Enroll members into cohort
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u_inst["id"], "role": "instructor"},
        headers=h_admin,
    )
    assert r.status_code == 201

    # Bulk enroll Alice (in cohort), leave Bob out
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/members",
        json={"user_id": u_alice["id"], "role": "learner"},
        headers=h_admin,
    )
    assert r.status_code == 201

    # Verify member count
    r = await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}", headers=h_admin)
    assert r.json()["data"]["member_count"] == 2

    # ═══════════════════════════════════════════════════════════
    # STEP 4: Create skills + exercises, assign to cohort
    # ═══════════════════════════════════════════════════════════
    cat = (
        await c.post(
            f"/api/v1/orgs/{oid}/categories", json={"name": "AI Production"}, headers=h_inst
        )
    ).json()["data"]["id"]

    sk = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "Prompt Engineering",
                "description": "Master AI prompt design for visual production",
                "difficulty": "intermediate",
                "category_id": cat,
            },
            headers=h_inst,
        )
    ).json()["data"]["id"]

    ex = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills/{sk}/exercises",
            json={
                "title": "Prompt Structure Quiz",
                "description": "MCQ on prompt best practices",
                "type": "multiple_choice",
                "config": {"correct": ["b"], "options": ["a", "b", "c"]},
                "max_score": 10,
            },
            headers=h_inst,
        )
    ).json()["data"]["id"]

    await c.post(f"/api/v1/orgs/{oid}/skills/{sk}/publish", headers=h_inst)

    # Assign skill to cohort
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/skills",
        json={"skill_id": sk},
        headers=h_inst,
    )
    assert r.status_code == 201

    # Alice completes the skill exercise
    r = await c.post(
        f"/api/v1/orgs/{oid}/exercises/{ex}/attempts",
        json={"answer": {"selected": ["b"]}},
        headers=h_alice,
    )
    assert r.status_code == 201
    assert r.json()["data"]["is_correct"] is True

    # ═══════════════════════════════════════════════════════════
    # STEP 5: Create Client Brief
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={
            "title": "Acme Corp Q4 Product Campaign",
            "client_name": "Acme Corporation",
            "client_industry": "Consumer Electronics",
            "project_type": "product_visualization",
            "objective": "Create hero images and social media assets for the Q4 product launch of the AcmeX Pro device",
            "target_audience": "Tech-savvy professionals aged 25-40",
            "tone_and_style": "Premium, modern, clean — Apple-inspired aesthetic",
            "deliverable_specs": [
                {
                    "name": "Hero Product Image",
                    "type": "image",
                    "description": "Main key visual for campaign landing page",
                    "required": False,
                },
                {
                    "name": "Campaign Tagline",
                    "type": "text",
                    "description": "Primary tagline + 2 alternatives",
                    "required": True,
                },
                {
                    "name": "Creative Prompt Documentation",
                    "type": "prompt",
                    "description": "All generation prompts used in creating the visuals",
                    "required": True,
                },
            ],
            "evaluation_criteria": [
                {"criterion": "Brand alignment", "weight": 0.3},
                {"criterion": "Commercial viability", "weight": 0.4},
            ],
            "budget_range": "$2,000-$5,000",
            "timeline": "3 weeks from assignment",
        },
        headers=h_inst,
    )
    assert r.status_code == 201
    brief = r.json()["data"]
    bid = brief["id"]
    assert brief["status"] == "draft"

    # ═══════════════════════════════════════════════════════════
    # STEP 6: Convert Brief → Commercial Project
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={
            "rubric": [
                {"criterion": "Brief Alignment", "max_score": 30},
                {"criterion": "Visual Quality", "max_score": 30},
                {"criterion": "Prompt Craftsmanship", "max_score": 20},
                {"criterion": "Commercial Readiness", "max_score": 20},
            ],
            "cohort_id": cid,
            "deadline": "2030-11-30T23:59:00Z",
        },
        headers=h_inst,
    )
    assert r.status_code == 201
    project = r.json()["data"]
    pid = project["id"]
    assert project["project_type"] == "ai_visual"

    # Brief should now be active
    brief_after = (await c.get(f"/api/v1/orgs/{oid}/briefs/{bid}", headers=h_inst)).json()["data"]
    assert brief_after["status"] == "active"

    # Publish the project
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/publish", headers=h_inst)
    assert r.status_code == 200

    # Verify deliverables were created from brief specs
    detail = (await c.get(f"/api/v1/orgs/{oid}/projects/{pid}", headers=h_inst)).json()["data"]
    assert len(detail["deliverables"]) == 3
    del_names = {d["name"] for d in detail["deliverables"]}
    assert "Hero Product Image" in del_names
    assert "Campaign Tagline" in del_names
    assert "Creative Prompt Documentation" in del_names

    # ═══════════════════════════════════════════════════════════
    # STEP 7: Assign project to cohort with deadline override
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/cohorts/{cid}/projects",
        json={
            "project_id": pid,
            "deadline_override": "2030-11-15T23:59:00Z",
            "max_submissions_override": 3,
            "participation_mode": "assigned",
        },
        headers=h_inst,
    )
    assert r.status_code == 201

    # ═══════════════════════════════════════════════════════════
    # STEP 8: Visibility — Alice sees project, Bob does NOT
    # ═══════════════════════════════════════════════════════════
    alice_projects = (await c.get(f"/api/v1/orgs/{oid}/projects", headers=h_alice)).json()["data"]
    alice_titles = {p["title"] for p in alice_projects}
    assert "Acme Corp Q4 Product Campaign" in alice_titles

    bob_projects = (await c.get(f"/api/v1/orgs/{oid}/projects", headers=h_bob)).json()["data"]
    bob_titles = {p["title"] for p in bob_projects}
    assert "Acme Corp Q4 Product Campaign" not in bob_titles

    # ═══════════════════════════════════════════════════════════
    # STEP 9: Application workflow (Bob applies to the brief)
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/apply",
        json={"note": "I completed all prerequisite skills and have portfolio work in this style"},
        headers=h_bob,
    )
    assert r.status_code == 201

    # Instructor reviews applications
    apps = (await c.get(f"/api/v1/orgs/{oid}/briefs/{bid}/applications", headers=h_inst)).json()[
        "data"
    ]
    assert len(apps) == 1
    assert apps[0]["user_name"] == "Bob Zhang"

    # Accept Bob's application
    r = await c.put(
        f"/api/v1/orgs/{oid}/briefs/{bid}/applications/{apps[0]['id']}",
        json={"status": "accepted"},
        headers=h_inst,
    )
    assert r.json()["data"]["status"] == "accepted"

    # ═══════════════════════════════════════════════════════════
    # STEP 10: Alice submits work
    # ═══════════════════════════════════════════════════════════
    sub = (await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions", headers=h_alice)).json()[
        "data"
    ]
    sid = sub["id"]

    # Fill in the required text deliverable (Campaign Tagline)
    tagline_del = next(d for d in detail["deliverables"] if d["name"] == "Campaign Tagline")
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
        json={
            "items": [
                {
                    "deliverable_id": tagline_del["id"],
                    "type": "text",
                    "content": "AcmeX Pro: Where Innovation Meets Precision",
                }
            ]
        },
        headers=h_alice,
    )
    assert r.status_code == 200

    # Fill in the prompt deliverable
    prompt_del = next(
        d for d in detail["deliverables"] if d["name"] == "Creative Prompt Documentation"
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/prompt-items",
        json={
            "deliverable_id": prompt_del["id"],
            "prompt": "Professional product photography of a sleek device, studio lighting, white background, 8K, commercial quality",
            "negative_prompt": "blurry, low quality, distorted",
            "model": "SDXL",
            "cfg_scale": 7.5,
            "steps": 30,
            "seed": 42,
        },
        headers=h_alice,
    )
    assert r.status_code == 201

    # Submit
    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h_alice)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"

    # ═══════════════════════════════════════════════════════════
    # STEP 11: AI Evaluation (mock LLM)
    # ═══════════════════════════════════════════════════════════
    await c.put(
        f"/api/v1/orgs/{oid}/settings/evaluation",
        json={"enabled": True, "monthly_budget_usd": 500},
        headers=h_admin,
    )

    class _MockResp:
        content = (
            '{"scores":['
            '{"criterion":"Brief Alignment","score":25,"max_score":30,"feedback":"Strong alignment with the Acme brief objectives"},'
            '{"criterion":"Visual Quality","score":22,"max_score":30,"feedback":"Clean execution, good lighting choices"},'
            '{"criterion":"Prompt Craftsmanship","score":18,"max_score":20,"feedback":"Well-structured prompt with appropriate parameters"},'
            '{"criterion":"Commercial Readiness","score":15,"max_score":20,"feedback":"Needs minor refinement for final delivery"}'
            '],"overall_feedback":"Solid commercial work with room for refinement in the final output",'
            '"strengths":["Brief alignment","Prompt engineering"],'
            '"improvements":["Final output polish","Brand color consistency"]}'
        )
        input_tokens = 800
        output_tokens = 300
        provider = "anthropic"
        model = "claude-sonnet-5"

    fake_llm = AsyncMock()
    fake_llm.complete = AsyncMock(return_value=_MockResp())
    with patch("app.services.evaluation.create_llm_client", return_value=fake_llm):
        r = await c.post(
            f"/api/v1/orgs/{oid}/evaluation/trigger",
            json={"submission_id": sid, "type": "submission_review"},
            headers=h_inst,
        )
    assert r.status_code == 201
    eval_task = r.json()["data"]
    assert eval_task["status"] == "completed"

    # ═══════════════════════════════════════════════════════════
    # STEP 12: Instructor sees AI feedback
    # ═══════════════════════════════════════════════════════════
    sub_detail = (
        await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h_inst)
    ).json()["data"]
    reviews = sub_detail["reviews"]
    assert len(reviews) >= 1
    ai_review = next(r for r in reviews if r["reviewer_type"] == "ai")
    assert ai_review["score"] == 80  # 25+22+18+15

    # ═══════════════════════════════════════════════════════════
    # STEP 13: Instructor requests revision
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={
            "status": "revision_requested",
            "score": 75,
            "feedback": "Good start — please refine the brand colors and add the product logo placement",
        },
        headers=h_inst,
    )
    assert r.status_code == 201

    sub_after = (
        await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h_alice)
    ).json()["data"]
    assert sub_after["status"] == "revision_requested"

    # ═══════════════════════════════════════════════════════════
    # STEP 14: Alice resubmits (revision round)
    # ═══════════════════════════════════════════════════════════
    # Update the tagline
    r = await c.put(
        f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}",
        json={
            "items": [
                {
                    "deliverable_id": tagline_del["id"],
                    "type": "text",
                    "content": "AcmeX Pro: Precision Engineered for Professionals",
                }
            ]
        },
        headers=h_alice,
    )
    assert r.status_code == 200

    r = await c.post(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}/submit", headers=h_alice)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "submitted"

    # ═══════════════════════════════════════════════════════════
    # STEP 15: Instructor approves with score override
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        f"/api/v1/orgs/{oid}/submissions/{sid}/reviews",
        json={
            "status": "approved",
            "score": 92,
            "feedback": "Excellent revision — ready for client delivery",
        },
        headers=h_inst,
    )
    assert r.status_code == 201

    sub_final = (
        await c.get(f"/api/v1/orgs/{oid}/projects/{pid}/submissions/{sid}", headers=h_inst)
    ).json()["data"]
    assert sub_final["status"] == "approved"
    assert sub_final["final_score"] == 92  # instructor override, not AI's 80

    # ═══════════════════════════════════════════════════════════
    # STEP 16: Cohort dashboard reflects correct state
    # ═══════════════════════════════════════════════════════════
    progress = (await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress", headers=h_inst)).json()[
        "data"
    ]
    assert progress["total_learners"] == 1
    assert progress["total_skills_assigned"] == 1
    assert len(progress["projects"]) >= 1

    proj_progress = next((p for p in progress["projects"] if p["project_id"] == pid), None)
    assert proj_progress is not None
    assert proj_progress["approved"] == 1
    assert proj_progress["not_started"] == 0

    # ═══════════════════════════════════════════════════════════
    # STEP 17: Learner drill-down shows Alice's progress
    # ═══════════════════════════════════════════════════════════
    drill = (
        await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/progress/{u_alice['id']}", headers=h_inst)
    ).json()["data"]
    assert drill["user_name"] == "Alice Chen"
    assert len(drill["skills"]) == 1
    assert drill["skills"][0]["name"] == "Prompt Engineering"
    assert drill["skills"][0]["status"] == "completed"
    assert len(drill["projects"]) >= 1
    alice_proj = next(p for p in drill["projects"] if p["project_id"] == pid)
    assert alice_proj["submission_status"] == "approved"
    assert alice_proj["score"] == 92

    # ═══════════════════════════════════════════════════════════
    # STEP 18: Alice's my-dashboard shows her cohort view
    # ═══════════════════════════════════════════════════════════
    my_dash = (
        await c.get(f"/api/v1/orgs/{oid}/cohorts/{cid}/my-dashboard", headers=h_alice)
    ).json()["data"]
    assert my_dash["cohort"]["name"] == "AI Visual Commerce — Fall 2026"
    assert len(my_dash["assigned_skills"]) == 1
    assert len(my_dash["assigned_projects"]) >= 1

    # ═══════════════════════════════════════════════════════════
    # STEP 19: Alice's my-cohorts lists this cohort
    # ═══════════════════════════════════════════════════════════
    my_cohorts = (await c.get(f"/api/v1/orgs/{oid}/my-cohorts", headers=h_alice)).json()["data"]
    assert any(co["id"] == cid for co in my_cohorts)

    # Bob is not in any cohort
    bob_cohorts = (await c.get(f"/api/v1/orgs/{oid}/my-cohorts", headers=h_bob)).json()["data"]
    assert len(bob_cohorts) == 0

    # ═══════════════════════════════════════════════════════════
    # STEP 20: Badge synced from skill completion
    # ═══════════════════════════════════════════════════════════
    badges = (await c.get("/api/v1/portfolio/badges", headers=h_alice)).json()["data"]
    assert any(b["skill_name"] == "Prompt Engineering" for b in badges)

    # ═══════════════════════════════════════════════════════════
    # STEP 21: Portfolio item from approved submission
    # ═══════════════════════════════════════════════════════════
    r = await c.post(
        "/api/v1/portfolio/items",
        json={
            "title": "Acme Q4 Campaign — Hero Visual",
            "submission_id": sid,
            "description": "Commercial work for Acme Corp Q4 product launch",
        },
        headers=h_alice,
    )
    assert r.status_code == 201
    item = r.json()["data"]
    assert item["score"] == 92
    assert item["source_project"] == "Acme Corp Q4 Product Campaign"

    # ═══════════════════════════════════════════════════════════
    # COMPLETE: Learning → Practice → Real Project → Evaluation
    #           → Delivery → Capability Proof
    # ═══════════════════════════════════════════════════════════
