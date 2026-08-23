"""Tests for learning + production composers (ADR-013, Issue #21 Parts E/F)."""

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
    return f"cmp-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Cmp"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"C-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


async def _skill_pack(c, h, oid, name, capabilities, minutes=30):
    """Create a published skill pack with given capability tags (own-org visible)."""
    r = await c.post(
        f"/api/v1/orgs/{oid}/packs",
        json={"name": name, "summary": "Test pack", "estimated_minutes": minutes},
        headers=h,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["data"]["id"]
    # Set capability tags + publish directly via DB (publish requires skills;
    # composer only needs PUBLISHED status + capability_tags)
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import PackStatus, SkillPack

    async with AsyncSessionLocal() as db:
        pack = await db.get(SkillPack, pid)
        pack.capability_tags = capabilities
        pack.status = PackStatus.PUBLISHED
        pack.estimated_minutes = minutes
        await db.commit()
    return pid


async def _confirmed_profile(c, h, oid, structured, context="learning"):
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": context, "structured_requirements": structured},
        headers=h,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["data"]["id"]
    r2 = await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=h)
    assert r2.status_code == 200
    return pid


def _wf_definition(capability="image_generation", output_type="image"):
    return {
        "schema_version": 1,
        "inputs": [{"key": "prompt_text", "type": "text", "required": True}],
        "outputs": [{"key": "result", "type": output_type, "from_step": "gen", "from_port": "out"}],
        "steps": [
            {
                "id": "take",
                "type": "asset_input",
                "name": "Take",
                "config": {"accept_types": ["image"]},
                "inputs": [],
                "outputs": [{"port": "prompt_text", "type": "text"}],
            },
            {
                "id": "gen",
                "type": "provider_action",
                "name": "Gen",
                "config": {"capability": capability},
                "inputs": [{"port": "p", "type": "prompt"}],
                "outputs": [{"port": "out", "type": output_type}],
            },
        ],
        "edges": [
            {"id": "e1", "from_step": "take", "from_port": "prompt_text", "to_step": "gen", "to_port": "p"}
        ],
        "ui": {},
    }


async def _wf_pack(c, h, oid, name, capability="image_generation", output_type="image", deps=None):
    r = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs", json={"name": name}, headers=h
    )
    pid = r.json()["data"]["id"]
    r2 = await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _wf_definition(capability, output_type)},
        headers=h,
    )
    assert r2.status_code == 200, r2.text
    body = {"version": "1.0.0"}
    if deps:
        body["dependencies"] = deps
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json=body, headers=h
    )
    assert r3.status_code == 201, r3.text
    return pid


# ── Learning composer ─────────────────────────────────────


@pytest.mark.asyncio
async def test_learning_compose_covers_capabilities(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    p1 = await _skill_pack(c, h, oid, "Upscale Basics", ["upscale"], minutes=30)
    p2 = await _skill_pack(c, h, oid, "BG Removal", ["background_removal"], minutes=40)

    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["upscale", "background_removal"]}
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    ids = [i["entity_id"] for i in payload["items"]]
    assert p1 in ids and p2 in ids
    assert payload["gaps"] == []
    assert payload["estimated_total_minutes"] == 70
    assert r.json()["data"]["engine_version"] == "1.0.0"


@pytest.mark.asyncio
async def test_learning_compose_gap_when_uncovered(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _skill_pack(c, h, oid, "Upscale Only", ["upscale"])
    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["upscale", "voice_generation"]}
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    gaps = r.json()["data"]["payload"]["gaps"]
    assert {"code": "NO_CONTENT_AVAILABLE", "capability": "voice_generation"} in gaps


@pytest.mark.asyncio
async def test_learning_compose_budget_truncation(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _skill_pack(c, h, oid, "Cheap Pack", ["upscale"], minutes=30)
    await _skill_pack(c, h, oid, "Expensive Pack", ["background_removal"], minutes=500)

    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {
            "required_capabilities": ["upscale", "background_removal"],
            "time_budget": 60,
        },
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    items = r.json()["data"]["payload"]["items"]
    statuses = {i["name"]: i["status"] for i in items}
    # Cheap fits; expensive is cut but KEPT in the payload (R8: nothing hidden)
    assert statuses["Cheap Pack"] == "included"
    assert statuses["Expensive Pack"] == "cut_for_budget"
    assert r.json()["data"]["payload"]["estimated_total_minutes"] == 30


@pytest.mark.asyncio
async def test_learning_confirm_materializes_with_placeholder_no_autoinstall(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _skill_pack(c, h, oid, "Not Installed Pack", ["upscale"])
    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    draft_id = r.json()["data"]["id"]

    # Count installations before confirm
    from sqlalchemy import func, select

    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPackInstallation

    async with AsyncSessionLocal() as db:
        before_r = await db.execute(
            select(func.count()).where(SkillPackInstallation.org_id == oid)
        )
        before = before_r.scalar_one()

    r2 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r2.status_code == 200, r2.text
    path_id = r2.json()["data"]["materialized_entity_id"]
    assert path_id

    # Path has a SECTION placeholder for the uninstalled pack
    r3 = await c.get(f"/api/v1/orgs/{oid}/paths/{path_id}/items", headers=h)
    if r3.status_code == 200:
        items = r3.json()["data"]
        assert any(
            i.get("item_type") == "section"
            and "Install pack" in (i.get("section_title") or "")
            for i in items
        ), items

    # NO auto-install happened (red line)
    async with AsyncSessionLocal() as db:
        after_r = await db.execute(
            select(func.count()).where(SkillPackInstallation.org_id == oid)
        )
        assert after_r.scalar_one() == before
    _ = pid


@pytest.mark.asyncio
async def test_compose_unconfirmed_profile_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {}},
        headers=h,
    )
    profile_id = r.json()["data"]["id"]  # NOT confirmed
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "PROFILE_NOT_CONFIRMED"


@pytest.mark.asyncio
async def test_double_confirm_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _skill_pack(c, h, oid, "Once Pack", ["upscale"])
    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    draft_id = r.json()["data"]["id"]
    r2 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r2.status_code == 200
    r3 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "DRAFT_ALREADY_CONFIRMED"


@pytest.mark.asyncio
async def test_update_draft_remove_items(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    p1 = await _skill_pack(c, h, oid, "Keep", ["upscale"])
    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    draft_id = r.json()["data"]["id"]
    r2 = await c.patch(
        f"/api/v1/orgs/{oid}/drafts/{draft_id}",
        json={"remove_entity_ids": [p1]},
        headers=h,
    )
    assert r2.status_code == 200
    items = r2.json()["data"]["payload"]["items"]
    assert all(i["status"] == "removed_by_user" for i in items if i["entity_id"] == p1)


# ── Production composer ───────────────────────────────────


@pytest.mark.asyncio
async def test_production_compose_chain_and_gaps(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # text_to_video scopes S2 so foreign PUBLIC packs from other test runs
    # are hard-excluded (shared dev DB)
    wf = await _wf_pack(
        c,
        h,
        oid,
        "Hero Gen",
        capability="text_to_video",
        output_type="video",
        deps={"requires_capabilities": [{"capability": "text_to_video", "features": []}]},
    )
    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"output_type": "video", "required_capabilities": ["text_to_video"]},
        context="production",
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    chain_ids = [w["entity_id"] for w in payload["workflow_chain"]]
    assert wf in chain_ids
    # No org offerings → NO_ELIGIBLE_PROVIDER gap surfaced
    assert any(g["code"] == "NO_ELIGIBLE_PROVIDER" for g in payload["gaps"])
    # Text input the user provides directly → needs_user_value placeholder
    assert any(p["reason"] == "needs_user_value" for p in payload["placeholders"])


@pytest.mark.asyncio
async def test_production_confirm_creates_project(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _wf_pack(c, h, oid, "Confirm Gen", output_type="image")
    # A template so materialization has something to instantiate
    rt = await c.post(
        f"/api/v1/orgs/{oid}/project-templates",
        json={
            "name": "Ad Template",
            "description": "Template desc",
            "instructions": "Do the thing",
            "rubric": [{"criterion": "Quality", "max_score": 100}],
        },
        headers=h,
    )
    assert rt.status_code == 201, rt.text

    profile_id = await _confirmed_profile(
        c, h, oid, {"output_type": "image"}, context="production"
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution",
        json={"profile_id": profile_id},
        headers=h,
    )
    draft = r.json()["data"]
    assert draft["payload"]["template"] is not None

    r2 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft['id']}/confirm", headers=h)
    assert r2.status_code == 200, r2.text
    project_id = r2.json()["data"]["materialized_entity_id"]

    r3 = await c.get(f"/api/v1/orgs/{oid}/projects/{project_id}", headers=h)
    assert r3.status_code == 200
    assert "Composed from workflows" in r3.json()["data"]["description"]


@pytest.mark.asyncio
async def test_draft_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    await _skill_pack(c, h1, o1, "Iso Pack", ["upscale"])
    profile_id = await _confirmed_profile(c, h1, o1, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{o1}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h1,
    )
    draft_id = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.get(f"/api/v1/orgs/{o2}/drafts/{draft_id}", headers=h2)
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_budget_cut_propagates_to_dependents(c):
    """A dependent must never stay included when its prerequisite was cut
    for budget — cuts propagate along prereq edges (audit HIGH 3)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # Big prerequisite (won't fit the budget) + small dependent (would fit)
    prereq_id = await _skill_pack(c, h, oid, "Big Prereq", ["upscale"], minutes=90)
    dep_id = await _skill_pack(c, h, oid, "Small Dependent", ["background_removal"], minutes=45)

    # Wire the dependency: dependent declares the prereq's slug
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPack

    async with AsyncSessionLocal() as db:
        prereq = await db.get(SkillPack, prereq_id)
        dep = await db.get(SkillPack, dep_id)
        dep.prerequisite_packs = [prereq.slug]
        await db.commit()

    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"required_capabilities": ["background_removal"], "time_budget": 60},
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    statuses = {i["entity_id"]: i["status"] for i in payload["items"]}
    # Prereq sorts first (topo) and exceeds the budget → cut
    assert statuses[prereq_id] == "cut_for_budget"
    # The dependent would fit (45 <= 60) but its prereq was cut → also cut
    assert statuses[dep_id] == "cut_for_budget"
    assert payload["estimated_total_minutes"] == 0


@pytest.mark.asyncio
async def test_composer_runs_record_no_impressions(c):
    """Composer-internal match runs must not write 'shown' feedback rows
    (audit LOW 4 — position-bias analytics pollution)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _skill_pack(c, h, oid, "Impression Pack", ["upscale"])
    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    run_id = r.json()["data"]["payload"]["match_run_id"]

    from sqlalchemy import select as _select

    from app.core.database import AsyncSessionLocal
    from app.models.matching import FeedbackEvent

    async with AsyncSessionLocal() as db:
        ev_r = await db.execute(
            _select(FeedbackEvent).where(
                FeedbackEvent.match_run_id == run_id,
                FeedbackEvent.event_type == "shown",
            )
        )
        assert list(ev_r.scalars().all()) == []


# ── Audit fixes (Issue #21 follow-up) ─────────────────────


@pytest.mark.asyncio
async def test_prereq_cycle_all_selected_fails_loudly(c):
    """A cycle whose members are ALL pre-selected bypasses the DFS path check
    (visit never recurses into known packs) — the post-Kahn check must raise
    PREREQ_CYCLE instead of silently dropping the packs (audit MEDIUM)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    a_id = await _skill_pack(c, h, oid, "Cycle A", ["upscale"])
    b_id = await _skill_pack(c, h, oid, "Cycle B", ["background_removal"])

    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPack

    async with AsyncSessionLocal() as db:
        a = await db.get(SkillPack, a_id)
        b = await db.get(SkillPack, b_id)
        a.prerequisite_packs = [b.slug]
        b.prerequisite_packs = [a.slug]
        await db.commit()

    # Require BOTH caps so the set cover selects both cycle members
    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["upscale", "background_removal"]}
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 422, r.text
    assert r.json()["error"]["code"] == "PREREQ_CYCLE"


@pytest.mark.asyncio
async def test_partial_completion_does_not_waive(c):
    """Waiving requires ALL of a pack's installed skills completed — one
    finished lesson must not drop the whole pack (audit MEDIUM 4)."""
    h, user = await _auth(c)
    oid = await _org(c, h)
    pack_id = await _skill_pack(c, h, oid, "Waiver Pack", ["upscale"])

    # Two org skills that originate from this pack
    cat = (
        await c.post(
            f"/api/v1/orgs/{oid}/categories",
            json={"name": f"WC-{uuid.uuid4().hex[:4]}"},
            headers=h,
        )
    ).json()["data"]["id"]
    skill_ids = []
    for i in range(2):
        r = await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": f"Waiver Skill {i}",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
            },
            headers=h,
        )
        skill_ids.append(r.json()["data"]["id"])

    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal
    from app.models.skill import ProgressStatus, SkillProgress

    async with AsyncSessionLocal() as db:
        for sid in skill_ids:
            await db.execute(
                text("UPDATE skills SET origin_pack_id = :p WHERE id = :id"),
                {"p": pack_id, "id": sid},
            )
        # Complete only the FIRST skill
        db.add(
            SkillProgress(
                org_id=oid,
                skill_id=skill_ids[0],
                user_id=user["id"],
                status=ProgressStatus.COMPLETED,
            )
        )
        await db.commit()

    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    items = {i["entity_id"]: i for i in r.json()["data"]["payload"]["items"]}
    assert items[pack_id]["status"] == "included"  # NOT waived

    # Complete the second skill → now fully done → waived
    async with AsyncSessionLocal() as db:
        db.add(
            SkillProgress(
                org_id=oid,
                skill_id=skill_ids[1],
                user_id=user["id"],
                status=ProgressStatus.COMPLETED,
            )
        )
        await db.commit()

    profile_id2 = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id2},
        headers=h,
    )
    items2 = {i["entity_id"]: i for i in r2.json()["data"]["payload"]["items"]}
    assert items2[pack_id]["status"] == "waived"


@pytest.mark.asyncio
async def test_extracted_time_budget_is_advisory_not_hard_cut(c):
    """An LLM-extracted time_budget must never drive cut_for_budget — it is
    demoted to _soft_time_budget and surfaced as a SOFT_TIME_BUDGET gap
    (R14 gray zone, audit MEDIUM)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _skill_pack(c, h, oid, "Big Pack", ["upscale"], minutes=90)

    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "learning",
            "structured_requirements": {
                "required_capabilities": ["upscale"],
                "time_budget": 60,
            },
        },
        headers=h,
    )
    profile_id = r.json()["data"]["id"]

    # Simulate extraction provenance for time_budget
    from sqlalchemy import text

    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        await db.execute(
            text(
                "UPDATE requirement_profiles SET extraction_meta = "
                """'{"provenance": {"required_capabilities": "user_entered", """
                """"time_budget": "extracted"}}'::jsonb WHERE id = :id"""
            ),
            {"id": profile_id},
        )
        await db.commit()

    await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{profile_id}/confirm", headers=h)
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r2.status_code == 201, r2.text
    payload = r2.json()["data"]["payload"]
    # 90-minute pack survives the 60-minute EXTRACTED budget (no hard cut)
    assert all(i["status"] != "cut_for_budget" for i in payload["items"])
    assert payload["estimated_total_minutes"] == 90
    assert any(g["code"] == "SOFT_TIME_BUDGET" for g in payload["gaps"])
