"""Cross-org IDOR / privacy sweep across ALL Issue #21 endpoint families (Part J)."""

import uuid
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture
async def c():
    from app.core.database import engine
    from app.main import app

    orig = app.router.lifespan_context

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


def _email():
    return f"sec-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Sec"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"S-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_cross_org_idor_sweep(c):
    """Org1 creates one resource of every Issue-21 family; org2 must get
    404/403 both through its own path and through org1's path."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    h2, _ = await _auth(c)
    o2 = await _org(c, h2)

    resources: dict[str, str] = {}

    # workflow pack
    r = await c.post(f"/api/v1/orgs/{o1}/workflow-packs", json={"name": "Sec Pack"}, headers=h1)
    resources["workflow-packs"] = r.json()["data"]["id"]

    # provider connection (mock, no creds)
    adapters = (await c.get("/api/v1/providers/adapters", headers=h1)).json()["data"]
    mock_id = next(a for a in adapters if a["key"] == "mock")["id"]
    r = await c.post(
        f"/api/v1/orgs/{o1}/provider-connections",
        json={"adapter_id": mock_id, "name": "Sec Conn"},
        headers=h1,
    )
    resources["provider-connections"] = r.json()["data"]["id"]

    # requirement profile
    r = await c.post(
        f"/api/v1/orgs/{o1}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {}},
        headers=h1,
    )
    resources["requirement-profiles"] = r.json()["data"]["id"]

    # comfyui import
    r = await c.post(
        f"/api/v1/orgs/{o1}/comfyui-imports",
        json={"data": '{"1": {"class_type": "KSampler", "inputs": {}}}', "encoding": "json"},
        headers=h1,
    )
    assert r.status_code == 201, r.text
    resources["comfyui-imports"] = r.json()["data"]["id"]

    # GET each via org2's path → 404; via org1's path as non-member → 403/404
    for family, rid in resources.items():
        r_own_path = await c.get(f"/api/v1/orgs/{o2}/{family}/{rid}", headers=h2)
        assert r_own_path.status_code == 404, f"{family} via org2 path: {r_own_path.status_code}"
        r_foreign = await c.get(f"/api/v1/orgs/{o1}/{family}/{rid}", headers=h2)
        assert r_foreign.status_code in (403, 404), f"{family} via org1 path: {r_foreign.status_code}"


@pytest.mark.asyncio
async def test_credential_never_leaks_anywhere(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    adapters = (await c.get("/api/v1/providers/adapters", headers=h)).json()["data"]
    anth_id = next(a for a in adapters if a["key"] == "anthropic")["id"]
    secret = f"sk-super-secret-{uuid.uuid4().hex}"
    r = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": anth_id, "name": "Leak Test", "credentials": {"api_key": secret}},
        headers=h,
    )
    conn_id = r.json()["data"]["id"]
    assert secret not in r.text

    # Sweep every provider read surface
    for path in (
        f"/api/v1/orgs/{oid}/provider-connections",
        f"/api/v1/orgs/{oid}/provider-connections/{conn_id}",
        f"/api/v1/orgs/{oid}/provider-offerings",
        "/api/v1/providers/adapters",
        "/api/v1/capabilities",
    ):
        resp = await c.get(path, headers=h)
        assert secret not in resp.text, f"credential leaked via {path}"


@pytest.mark.asyncio
async def test_match_results_exclude_inaccessible_entities(c):
    """Org2's match must not surface org1's private packs even as excluded.

    Airtight variant: the requirement is scoped so the hidden pack would be
    the TOP candidate were it eligible (required capability + an exclusive
    scenario tag no other pack can have) — an empty-requirement query would
    let a leaked pack hide below the top-50 truncation on a shared DB and
    the assertion would pass without exercising the S1 filter at all."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    scenario = f"exclusive-scenario-{uuid.uuid4().hex}"
    r = await c.post(
        f"/api/v1/orgs/{o1}/workflow-packs",
        json={"name": f"Hidden Pack {uuid.uuid4().hex[:8]}"},
        headers=h1,
    )
    hidden_id = r.json()["data"]["id"]
    # Publish but PRIVATE, with a capability + exclusive scenario that make it
    # score strictly above every other pack for the query below
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import PackStatus
    from app.models.workflow_pack import WorkflowPack

    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, hidden_id)
        pack.status = PackStatus.PUBLISHED
        pack.capability_tags = ["multimodal_review"]
        pack.scenario_tags = [scenario]
        await db.commit()

    structured = {
        "required_capabilities": ["multimodal_review"],
        "scenario": scenario,
    }

    # Sanity (self-validating test): the OWNER org's match ranks the pack #1 —
    # capability 1.0 + exclusive scenario 1.0 beat any rival's best possible
    # score. So if the S1 org-visibility filter leaked, org2's run below
    # would rank it #1 too and the absence assertions would fail.
    rp1 = await c.post(
        f"/api/v1/orgs/{o1}/requirement-profiles",
        json={"context_type": "production", "structured_requirements": structured},
        headers=h1,
    )
    pid1 = rp1.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{o1}/requirement-profiles/{pid1}/confirm", headers=h1)
    rm1 = await c.post(
        f"/api/v1/orgs/{o1}/match",
        json={"requirement_profile_id": pid1, "target_entity_type": "workflow_pack", "limit": 50},
        headers=h1,
    )
    assert rm1.status_code == 200, rm1.text
    own_ranked = [x["entity_id"] for x in rm1.json()["data"]["results"]]
    assert own_ranked and own_ranked[0] == hidden_id

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    rp = await c.post(
        f"/api/v1/orgs/{o2}/requirement-profiles",
        json={"context_type": "production", "structured_requirements": structured},
        headers=h2,
    )
    pid = rp.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{o2}/requirement-profiles/{pid}/confirm", headers=h2)
    rm = await c.post(
        f"/api/v1/orgs/{o2}/match",
        json={"requirement_profile_id": pid, "target_entity_type": "workflow_pack", "limit": 50},
        headers=h2,
    )
    assert rm.status_code == 200, rm.text
    data = rm.json()["data"]
    all_ids = [x["entity_id"] for x in data["results"]] + [
        x["entity_id"] for x in data["excluded"]
    ]
    assert hidden_id not in all_ids

    # S1 exclusion means it never becomes a candidate at all — it must appear
    # NOWHERE: not in the persisted result rows either. And because the pack
    # SATISFIES every hard constraint of this query, a leaked candidate could
    # only land in ranked results (rank #1) — it cannot hide inside
    # excluded_count, so the absence above also proves excluded_count does
    # not include it.
    from sqlalchemy import select

    from app.models.matching import MatchResult

    async with AsyncSessionLocal() as db:
        rows_r = await db.execute(
            select(MatchResult.entity_id).where(MatchResult.match_run_id == data["id"])
        )
        persisted_ids = {row[0] for row in rows_r.all()}
    assert hidden_id not in persisted_ids


@pytest.mark.asyncio
async def test_definition_data_uri_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "URI Pack"}, headers=h)
    pack_id = r.json()["data"]["id"]
    bad = {
        "schema_version": 1,
        "inputs": [],
        "outputs": [],
        "steps": [
            {
                "id": "bad",
                "type": "instruction",
                "name": "Bad",
                "config": {"content": "data:image/png;base64,AAAA"},
                "inputs": [],
                "outputs": [],
            }
        ],
        "edges": [],
        "ui": {},
    }
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pack_id}/definition",
        json={"definition": bad},
        headers=h,
    )
    assert r2.status_code == 422
    codes = {d["code"] for d in r2.json()["error"]["details"]}
    assert "WF_DATA_URI_REJECTED" in codes


@pytest.mark.asyncio
async def test_student_role_restrictions(c):
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    h_student, student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": student["id"], "role": "student"},
        headers=h_owner,
    )
    # Packs
    r1 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "Student Pack"}, headers=h_student
    )
    assert r1.status_code == 403
    # Connections
    adapters = (await c.get("/api/v1/providers/adapters", headers=h_student)).json()["data"]
    mock_id = next(a for a in adapters if a["key"] == "mock")["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/provider-connections",
        json={"adapter_id": mock_id, "name": "Student Conn"},
        headers=h_student,
    )
    assert r2.status_code == 403
    # Drafts
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": "01AAAAAAAAAAAAAAAAAAAAAAAA"},
        headers=h_student,
    )
    assert r3.status_code == 403


@pytest.mark.asyncio
async def test_match_run_and_draft_cross_org(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    rp = await c.post(
        f"/api/v1/orgs/{o1}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {}},
        headers=h1,
    )
    pid = rp.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{o1}/requirement-profiles/{pid}/confirm", headers=h1)
    rm = await c.post(
        f"/api/v1/orgs/{o1}/match",
        json={"requirement_profile_id": pid, "target_entity_type": "skill_pack"},
        headers=h1,
    )
    run_id = rm.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r = await c.get(f"/api/v1/orgs/{o2}/match-runs/{run_id}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_workflow_run_step_review_cross_org(c):
    """Reviews and runs are unreachable across orgs (uses direct DB seed)."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)

    from datetime import UTC, datetime, timedelta

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import (
        StepRunStatus,
        WorkflowRun,
        WorkflowStepReview,
        WorkflowStepRun,
    )

    async with AsyncSessionLocal() as db:
        run = WorkflowRun(org_id=o1, definition_snapshot={"steps": []}, inputs={})
        db.add(run)
        await db.flush()
        sr = WorkflowStepRun(
            run_id=run.id,
            step_id="gate",
            step_type="review_gate",
            status=StepRunStatus.WAITING_REVIEW,
        )
        db.add(sr)
        await db.flush()
        review = WorkflowStepReview(
            step_run_id=sr.id, org_id=o1, due_at=datetime.now(UTC) + timedelta(days=7)
        )
        db.add(review)
        await db.commit()
        run_id, review_id = run.id, review.id

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r1 = await c.get(f"/api/v1/orgs/{o2}/workflow-runs/{run_id}", headers=h2)
    assert r1.status_code == 404
    r2 = await c.post(
        f"/api/v1/orgs/{o2}/step-reviews/{review_id}/decide",
        json={"decision": "approved"},
        headers=h2,
    )
    assert r2.status_code == 404
    # Cancel across orgs also blocked
    r3 = await c.post(f"/api/v1/orgs/{o2}/workflow-runs/{run_id}/cancel", headers=h2)
    assert r3.status_code == 404


@pytest.mark.asyncio
async def test_delete_org_archives_workflow_packs(c):
    """Deleting an org must archive its workflow packs too — otherwise a
    dead org's PUBLIC packs stay live and installable (audit HIGH 1)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Publish + approve a PUBLIC workflow pack
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "Zombie Pack"}, headers=h)
    pid = r.json()["data"]["id"]
    definition = {
        "schema_version": 1,
        "inputs": [{"key": "topic", "type": "text", "required": True}],
        "outputs": [{"key": "final", "type": "image", "from_step": "gen", "from_port": "result"}],
        "steps": [
            {
                "id": "gen",
                "type": "provider_action",
                "name": "Gen",
                "config": {"capability": "image_generation"},
                "inputs": [],
                "outputs": [{"port": "result", "type": "image"}],
            }
        ],
        "edges": [],
        "ui": {},
    }
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": definition},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/submit-review", headers=h)
    await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/approve", headers=h)

    # Visible in the public registry before deletion
    r1 = await c.get(f"/api/v1/registry/workflow-packs/{pid}")
    assert r1.status_code == 200

    # Delete the org
    r2 = await c.delete(f"/api/v1/orgs/{oid}", headers=h)
    assert r2.status_code == 204

    # Pack is archived: gone from registry detail AND not installable elsewhere
    r3 = await c.get(f"/api/v1/registry/workflow-packs/{pid}")
    assert r3.status_code == 404

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r4 = await c.post(
        f"/api/v1/orgs/{o2}/workflow-installations", json={"pack_id": pid}, headers=h2
    )
    assert r4.status_code == 404


@pytest.mark.asyncio
async def test_student_cannot_decide_step_review(c):
    """decide_review approves real provider work — students must not
    self-approve (audit MEDIUM 14)."""
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    h_student, student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": student["id"], "role": "student"},
        headers=h_owner,
    )

    from datetime import UTC, datetime, timedelta

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_run import (
        RunStatus,
        StepRunStatus,
        WorkflowRun,
        WorkflowStepReview,
        WorkflowStepRun,
    )

    async with AsyncSessionLocal() as db:
        run = WorkflowRun(
            org_id=oid,
            definition_snapshot={"steps": []},
            inputs={},
            status=RunStatus.WAITING_REVIEW,
        )
        db.add(run)
        await db.flush()
        sr = WorkflowStepRun(
            run_id=run.id,
            step_id="gate",
            step_type="review_gate",
            status=StepRunStatus.WAITING_REVIEW,
        )
        db.add(sr)
        await db.flush()
        review = WorkflowStepReview(
            step_run_id=sr.id, org_id=oid, due_at=datetime.now(UTC) + timedelta(days=7)
        )
        db.add(review)
        await db.commit()
        review_id = review.id

    # Student blocked
    r = await c.post(
        f"/api/v1/orgs/{oid}/step-reviews/{review_id}/decide",
        json={"decision": "approved"},
        headers=h_student,
    )
    assert r.status_code == 403

    # Owner allowed
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/step-reviews/{review_id}/decide",
        json={"decision": "approved"},
        headers=h_owner,
    )
    assert r2.status_code == 200


@pytest.mark.asyncio
async def test_workflow_pack_path_item_progress_no_crash(c):
    """get_path_progress must tolerate WORKFLOW_PACK items — they were added
    to the enum without a progress branch (audit finding 16)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    path_id = (
        await c.post(f"/api/v1/orgs/{oid}/paths", json={"name": "WF Path"}, headers=h)
    ).json()["data"]["id"]

    # A regular skill item so there's real progress to compute
    cat = (
        await c.post(
            f"/api/v1/orgs/{oid}/categories", json={"name": f"PC-{uuid.uuid4().hex[:4]}"}, headers=h
        )
    ).json()["data"]["id"]
    skill_id = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": "WF Path Skill",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
    ).json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{oid}/paths/{path_id}/items",
        json={"item_type": "skill", "skill_id": skill_id},
        headers=h,
    )

    # Insert a WORKFLOW_PACK item directly (creation API is out of scope)
    from app.core.database import AsyncSessionLocal
    from app.models.learning_path import LearningPathItem, PathItemType

    async with AsyncSessionLocal() as db:
        db.add(
            LearningPathItem(
                path_id=path_id,
                item_type=PathItemType.WORKFLOW_PACK,
                workflow_pack_id="01AAAAAAAAAAAAAAAAAAAAAAAA",
                sort_order=99,
            )
        )
        await db.commit()

    r = await c.get(f"/api/v1/orgs/{oid}/paths/{path_id}/my-progress", headers=h)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    types = {i["type"] for i in data["items"]}
    assert "workflow_pack" in types
    # Both items count as required; neither is done
    assert data["total_required"] == 2
    assert data["completed"] == 0


@pytest.mark.asyncio
async def test_shortlist_forbidden_to_plain_members(c):
    """Part J: private learner evidence must not be exposed to unauthorized
    users. The creator shortlist carries per-capability evidence details —
    a plain MEMBER (student) must get 403, not the org's evidence graph."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # Create a project to shortlist against
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Sec Project",
            "description": "d",
            "instructions": "deliver",
            "rubric": [{"criterion": "Quality", "max_score": 100}],
            "project_type": "ai_visual",
        },
        headers=h,
    )
    project_id = r.json()["data"]["id"]
    # A confirmed profile
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "talent_matching", "structured_requirements": {"goal": "match"}},
        headers=h,
    )
    profile_id = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{profile_id}/confirm", headers=h)
    # Student member (direct add — same pattern as test_creator_matching)
    h2, user2 = await _auth(c)
    r = await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": user2["id"], "role": "student"},
        headers=h,
    )
    assert r.status_code in (200, 201), r.text[:200]
    r = await c.get(
        f"/api/v1/orgs/{oid}/projects/{project_id}/creator-shortlist",
        params={"profile_id": profile_id},
        headers=h2,
    )
    assert r.status_code == 403, f"{r.status_code}: {r.text[:200]}"


@pytest.mark.asyncio
async def test_shortlist_exposes_no_protected_attributes(c):
    """Part J: creator matching never uses or exposes protected/sensitive
    personal attributes — the shortlist payload carries only entity_id,
    display name, rank/score/tier, reasons/gaps, and evidence rows. No
    email, no last_login, no role, no PII fields."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Attr Project",
            "description": "d",
            "instructions": "deliver",
            "rubric": [{"criterion": "Quality", "max_score": 100}],
            "project_type": "ai_visual",
        },
        headers=h,
    )
    project_id = r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "talent_matching", "structured_requirements": {"goal": "match"}},
        headers=h,
    )
    profile_id = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{profile_id}/confirm", headers=h)
    r = await c.get(
        f"/api/v1/orgs/{oid}/projects/{project_id}/creator-shortlist",
        params={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 200, r.text[:300]
    body = r.text.lower()
    for forbidden in ("email", "last_login", "password", "\"role\""):
        assert forbidden not in body, f"shortlist response leaks '{forbidden}'"
    # Structural check: every result carries only the declared fields
    allowed = {"entity_id", "name", "rank", "score", "tier", "reasons", "gaps", "evidence"}
    for entry in r.json()["data"]["results"]:
        assert set(entry.keys()) <= allowed, set(entry.keys()) - allowed


# ── R26: authorization correctness matrix (role enforcement, not just presence) ──


async def _member(c, owner_h, oid, role):
    """Register a fresh user and add them to the org at the given role."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": f"Role{role[:3]}"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}
    rr = await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": d["user"]["id"], "role": role},
        headers=owner_h,
    )
    assert rr.status_code in (200, 201), rr.text
    return h


@pytest.mark.asyncio
async def test_authz_matrix_write_endpoints_enforce_roles(c):
    """R26: guards must enforce the RIGHT role, not merely be present.
    WRITE_ROLES = owner/admin/instructor; provider connections = admin only;
    a student must be 403 on write endpoints; a non-member always 403/404."""
    owner, _ = await _auth(c)
    oid = await _org(c, owner)
    admin = await _member(c, owner, oid, "admin")
    instructor = await _member(c, owner, oid, "instructor")
    student = await _member(c, owner, oid, "student")
    nonmember, _ = await _auth(c)

    async def code(h, method, path, body=None):
        r = await c.request(method, f"/api/v1/orgs/{oid}{path}", json=body, headers=h)
        return r.status_code

    # WRITE_ROLES endpoint: create workflow pack
    assert await code(owner, "POST", "/workflow-packs", {"name": "Ap"}) == 201
    assert await code(instructor, "POST", "/workflow-packs", {"name": "Bp"}) == 201
    assert await code(student, "POST", "/workflow-packs", {"name": "Cp"}) == 403
    assert await code(nonmember, "POST", "/workflow-packs", {"name": "Dp"}) in (403, 404)

    # ADMIN-only endpoint: create provider connection (instructor must be 403)
    assert await code(admin, "POST", "/provider-connections",
                      {"adapter_id": "01JFAKE0000000000000000000", "name": "Cx"}) in (404, 422)  # passes authz, fails on fake adapter
    assert await code(instructor, "POST", "/provider-connections",
                      {"adapter_id": "01JFAKE0000000000000000000", "name": "Cy"}) == 403
    assert await code(student, "POST", "/provider-connections",
                      {"adapter_id": "01JFAKE0000000000000000000", "name": "Cz"}) == 403

    # Any-member endpoint: create requirement profile (student allowed)
    assert await code(student, "POST", "/requirement-profiles",
                      {"context_type": "learning", "structured_requirements": {"goal": "g"}}) == 201
    assert await code(nonmember, "POST", "/requirement-profiles",
                      {"context_type": "learning", "structured_requirements": {"goal": "g"}}) in (403, 404)


@pytest.mark.asyncio
async def test_authz_profile_owner_isolation(c):
    """R26: a member cannot confirm or edit ANOTHER member's requirement
    profile (would turn their unconfirmed extractions into hard constraints
    they never approved); an instructor may act on behalf."""
    owner, _ = await _auth(c)
    oid = await _org(c, owner)
    s1 = await _member(c, owner, oid, "student")
    s2 = await _member(c, owner, oid, "student")
    instructor = await _member(c, owner, oid, "instructor")

    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "mine"}},
        headers=s1,
    )
    pid = r.json()["data"]["id"]

    # s2 confirm/patch s1's profile → 403 PROFILE_FORBIDDEN
    rc = await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=s2)
    assert rc.status_code == 403 and rc.json()["error"]["code"] == "PROFILE_FORBIDDEN"
    rp = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"goal": "hijacked"}},
        headers=s2,
    )
    assert rp.status_code == 403 and rp.json()["error"]["code"] == "PROFILE_FORBIDDEN"

    # instructor may confirm on the learner's behalf
    ri = await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=instructor)
    assert ri.status_code == 200, ri.text
