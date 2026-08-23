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
    """Org2's match must not surface org1's private packs even as excluded."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    r = await c.post(
        f"/api/v1/orgs/{o1}/workflow-packs", json={"name": "Hidden Pack"}, headers=h1
    )
    hidden_id = r.json()["data"]["id"]
    # Publish but PRIVATE
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import PackStatus
    from app.models.workflow_pack import WorkflowPack

    async with AsyncSessionLocal() as db:
        pack = await db.get(WorkflowPack, hidden_id)
        pack.status = PackStatus.PUBLISHED
        await db.commit()

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    rp = await c.post(
        f"/api/v1/orgs/{o2}/requirement-profiles",
        json={"context_type": "production", "structured_requirements": {}},
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
