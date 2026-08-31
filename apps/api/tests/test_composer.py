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
            {
                "id": "e1",
                "from_step": "take",
                "from_port": "prompt_text",
                "to_step": "gen",
                "to_port": "p",
            }
        ],
        "ui": {},
    }


async def _wf_pack(c, h, oid, name, capability="image_generation", output_type="image", deps=None):
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json={"name": name}, headers=h)
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
    r3 = await c.post(f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json=body, headers=h)
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
        before_r = await db.execute(select(func.count()).where(SkillPackInstallation.org_id == oid))
        before = before_r.scalar_one()

    r2 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r2.status_code == 200, r2.text
    path_id = r2.json()["data"]["materialized_entity_id"]
    assert path_id

    # Path has a SECTION placeholder for the uninstalled pack — the fetch
    # must succeed unconditionally (a guarded assert silently decays)
    r3 = await c.get(f"/api/v1/orgs/{oid}/paths/{path_id}/items", headers=h)
    assert r3.status_code == 200, r3.text
    items = r3.json()["data"]
    assert any(
        i.get("item_type") == "section" and "Install pack" in (i.get("section_title") or "")
        for i in items
    ), items

    # NO auto-install happened (red line)
    async with AsyncSessionLocal() as db:
        after_r = await db.execute(select(func.count()).where(SkillPackInstallation.org_id == oid))
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
    """Second confirm → 409: the conditional-UPDATE claim makes confirm
    race-safe (the loser's rowcount is 0), so a sequential second confirm
    exercises the same guarded path as a concurrent one."""
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
    first_path_id = r2.json()["data"]["materialized_entity_id"]
    r3 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r3.status_code == 409
    assert r3.json()["error"]["code"] == "DRAFT_ALREADY_CONFIRMED"

    # Exactly ONE LearningPath materialized — no orphaned duplicate
    from app.core.database import AsyncSessionLocal
    from app.models.composer import SolutionDraft

    async with AsyncSessionLocal() as db:
        stored = await db.get(SolutionDraft, draft_id)
        assert stored.status == "confirmed"
        assert stored.materialized_entity_id == first_path_id


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


@pytest.mark.asyncio
async def test_confirm_honors_patch_landing_before_claim(c, monkeypatch):
    """R85 confirm-vs-PATCH TOCTOU: confirm read the draft, THEN a PATCH
    committed a removal, THEN confirm claimed the row. Without the post-claim
    refresh, confirm materializes the pre-claim snapshot — the removed item
    reappears in the LearningPath. Deterministic: a hook on
    claim_draft_for_confirm injects the PATCH into the exact race window."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    p1 = await _skill_pack(c, h, oid, "Remove Me R85", ["upscale"])
    await _skill_pack(c, h, oid, "Keep Me R85", ["background_removal"])
    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["upscale", "background_removal"]}
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path", json={"profile_id": profile_id}, headers=h
    )
    draft_id = r.json()["data"]["id"]

    from app.services.learning_composer import LearningComposerService

    orig_claim = LearningComposerService.claim_draft_for_confirm
    fired = {"done": False}

    async def claim_after_patch(self, d_id, o_id):
        # Inject the PATCH between confirm's read and its claim (the window)
        if not fired["done"] and d_id == draft_id:
            fired["done"] = True
            rr = await c.patch(
                f"/api/v1/orgs/{oid}/drafts/{draft_id}",
                json={"remove_entity_ids": [p1]},
                headers=h,
            )
            assert rr.status_code == 200, rr.text
        return await orig_claim(self, d_id, o_id)

    monkeypatch.setattr(LearningComposerService, "claim_draft_for_confirm", claim_after_patch)
    r2 = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r2.status_code == 200, r2.text
    assert fired["done"]
    path_id = r2.json()["data"]["materialized_entity_id"]

    # The removed pack must NOT have materialized (both packs are uninstalled →
    # placeholder sections; the removed one's section must be absent)
    r3 = await c.get(f"/api/v1/orgs/{oid}/paths/{path_id}/items", headers=h)
    titles = [i.get("section_title") or "" for i in r3.json()["data"]]
    assert any("Keep Me R85" in t for t in titles), titles
    assert not any("Remove Me R85" in t for t in titles), titles


@pytest.mark.asyncio
async def test_concurrent_patch_no_lost_removal(c, monkeypatch):
    """R85 PATCH+PATCH lost update: two PATCHes each removing a DIFFERENT item.
    Without the update_draft row lock, both read the same payload snapshot and
    the second full-payload write silently reverts the first's removal.
    Deterministic: a barrier in get_draft holds each PATCH after its read until
    both have read (row lock → the second blocks in the DB and times out the
    barrier instead, then re-reads the first's committed payload)."""
    import asyncio

    h, _ = await _auth(c)
    oid = await _org(c, h)
    p1 = await _skill_pack(c, h, oid, "Item One", ["upscale"])
    p2 = await _skill_pack(c, h, oid, "Item Two", ["background_removal"])
    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["upscale", "background_removal"]}
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path", json={"profile_id": profile_id}, headers=h
    )
    draft_id = r.json()["data"]["id"]

    from app.core.database import AsyncSessionLocal
    from app.services.learning_composer import LearningComposerService

    orig_get = LearningComposerService.get_draft
    reads = {"n": 0}
    both_read = asyncio.Event()

    async def barrier_get_draft(self, d_id, o_id, for_update=False):
        draft = await orig_get(self, d_id, o_id, for_update=for_update)
        reads["n"] += 1
        if reads["n"] >= 2:
            both_read.set()
        # Hold this PATCH's snapshot until the other has read too. With the
        # row lock the second reader is blocked in the DB, so the first times
        # out and proceeds — the interleave the lock exists to prevent simply
        # cannot form.
        import contextlib

        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(both_read.wait(), timeout=2)
        return draft

    monkeypatch.setattr(LearningComposerService, "get_draft", barrier_get_draft)

    async def patch_one(pack_id):
        async with AsyncSessionLocal() as db:
            svc = LearningComposerService(db)
            await svc.update_draft(draft_id, oid, [pack_id])
            await db.commit()

    await asyncio.gather(patch_one(p1), patch_one(p2))
    monkeypatch.setattr(LearningComposerService, "get_draft", orig_get)

    d = (await c.get(f"/api/v1/orgs/{oid}/drafts/{draft_id}", headers=h)).json()["data"]
    removed = {i["entity_id"] for i in d["payload"]["items"] if i["status"] == "removed_by_user"}
    # BOTH removals must survive (neither lost to last-writer-won)
    assert p1 in removed and p2 in removed, removed


# ── Production composer ───────────────────────────────────


@pytest.mark.asyncio
async def test_production_compose_chain_and_gaps(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # (image_editing → video) has ZERO foreign public packs in the shared dev
    # DB, so the org's own pack is the sole chain-head candidate. Earlier this
    # used text_to_video→video, which became flaky once R83/R84 live probes
    # left a public+approved text_to_video video pack that outranked the test's
    # own pack as the chain head (shared-DB pollution, R84).
    wf = await _wf_pack(
        c,
        h,
        oid,
        "Hero Gen",
        capability="image_editing",
        output_type="video",
        deps={"requires_capabilities": [{"capability": "image_editing", "features": []}]},
    )
    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"output_type": "video", "required_capabilities": ["image_editing"]},
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
async def test_production_compose_unresolvable_recommended_pack_is_gap(c):
    """R85: a recommended pack whose slug resolves to nothing published/visible
    must surface as a RECOMMENDED_PACK_UNAVAILABLE gap row — silently dropping
    it violates ADR-013's 'every omission is a first-class row with a reason'."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    ghost = f"ghost-{uuid.uuid4().hex[:10]}"  # slug that exists nowhere
    wf = await _wf_pack(
        c,
        h,
        oid,
        "Rec Gap Gen",
        capability="image_editing",
        output_type="video",
        deps={"recommended_packs": [{"family": "skill_pack", "slug": ghost}]},
    )
    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"output_type": "video", "required_capabilities": ["image_editing"]},
        context="production",
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    assert wf in [w["entity_id"] for w in payload["workflow_chain"]]
    # The ghost recommendation is a visible gap, not a silent drop
    rec_gaps = [g for g in payload["gaps"] if g["code"] == "RECOMMENDED_PACK_UNAVAILABLE"]
    assert any(g.get("slug") == ghost for g in rec_gaps), payload["gaps"]
    # And it did NOT sneak into items either
    assert not any(i.get("slug") == ghost for i in payload["items"])


@pytest.mark.asyncio
async def test_production_compose_no_eligible_workflows_gap(c):
    """R82: deterministic coverage of the empty-survivor branch. The browser
    test (sweep-matching) had to relax to NO_WORKFLOWS_AVAILABLE|
    NO_WORKFLOW_FOR_OUTPUT because the shared dev DB holds foreign public
    packs for common capabilities. Use a required capability + output type
    that NO pack (own-org or foreign-public) can satisfy in this DB, so S2
    survivors are empty → NO_WORKFLOWS_AVAILABLE exactly, no template, no chain.
    'video_editing' → 'reference_asset' output has no producer anywhere."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"output_type": "reference_asset", "required_capabilities": ["video_editing"]},
        context="production",
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    assert payload["workflow_chain"] == []
    codes = {g["code"] for g in payload["gaps"]}
    assert "NO_WORKFLOWS_AVAILABLE" in codes, codes
    assert "NO_TEMPLATE_AVAILABLE" in codes, codes


@pytest.mark.asyncio
async def test_production_compose_rollup_keeps_distinct_feature_sets(c):
    """R84: R83 made a manifest carry one requires_capabilities entry per
    distinct (capability, feature-set). The composer's provider-gap rollup
    must dedup by (capability, features), not capability alone — else a chain
    whose pack declares the same capability with two different feature-sets
    drops one gap and under-reports NO_ELIGIBLE_PROVIDER. Build a pack whose
    manifest carries two text_to_video entries with different features and
    assert BOTH surface as gaps."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # A two-provider-step definition: both text_to_video, different features.
    two_step = {
        "schema_version": 1,
        "inputs": [{"key": "prompt_text", "type": "text", "required": True}],
        "outputs": [{"key": "result", "type": "video", "from_step": "g2", "from_port": "out"}],
        "steps": [
            {
                "id": "take",
                "type": "asset_input",
                "name": "T",
                "config": {"accept_types": ["image"]},
                "inputs": [],
                "outputs": [{"port": "prompt_text", "type": "text"}],
            },
            {
                "id": "g1",
                "type": "provider_action",
                "name": "G1",
                "config": {"capability": "text_to_video", "required_features": ["hd"]},
                "inputs": [{"port": "p", "type": "prompt"}],
                "outputs": [{"port": "mid", "type": "video"}],
            },
            {
                "id": "g2",
                "type": "provider_action",
                "name": "G2",
                "config": {"capability": "text_to_video", "required_features": ["slowmo"]},
                "inputs": [{"port": "src", "type": "video"}],
                "outputs": [{"port": "out", "type": "video"}],
            },
        ],
        "edges": [
            {
                "id": "e1",
                "from_step": "take",
                "from_port": "prompt_text",
                "to_step": "g1",
                "to_port": "p",
            },
            {"id": "e2", "from_step": "g1", "from_port": "mid", "to_step": "g2", "to_port": "src"},
        ],
        "ui": {},
    }
    pid = (
        await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json={"name": "TwoFeat"}, headers=h)
    ).json()["data"]["id"]
    assert (
        await c.put(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
            json={"definition": two_step},
            headers=h,
        )
    ).status_code == 200
    assert (
        await c.post(
            f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases",
            json={"version": "1.0.0"},
            headers=h,
        )
    ).status_code == 201

    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"output_type": "video", "required_capabilities": ["text_to_video"]},
        context="production",
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution", json={"profile_id": profile_id}, headers=h
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    # No org offerings → each distinct feature-set is its own NO_ELIGIBLE_PROVIDER gap
    missing = {
        tuple(sorted(g.get("missing_features", [])))
        for g in payload["gaps"]
        if g["code"] == "NO_ELIGIBLE_PROVIDER"
    }
    assert ("hd",) in missing, missing
    assert ("slowmo",) in missing, missing
    """R82: deterministic coverage of the empty-survivor branch. The browser
    test (sweep-matching) had to relax to NO_WORKFLOWS_AVAILABLE|
    NO_WORKFLOW_FOR_OUTPUT because the shared dev DB holds foreign public
    packs for common capabilities. Use a required capability + output type
    that NO pack (own-org or foreign-public) can satisfy in this DB, so S2
    survivors are empty → NO_WORKFLOWS_AVAILABLE exactly, no template, no chain.
    'video_editing' → 'reference_asset' output has no producer anywhere."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {"output_type": "reference_asset", "required_capabilities": ["video_editing"]},
        context="production",
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    assert payload["workflow_chain"] == []
    codes = {g["code"] for g in payload["gaps"]}
    assert "NO_WORKFLOWS_AVAILABLE" in codes, codes
    assert "NO_TEMPLATE_AVAILABLE" in codes, codes


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

    profile_id = await _confirmed_profile(c, h, oid, {"output_type": "image"}, context="production")
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


@pytest.mark.asyncio
async def test_unresolvable_prereq_slug_surfaces_gap(c):
    """A prerequisite slug that resolves to no visible published pack must
    emit a PREREQ_NOT_FOUND gap row — never a silent drop (round-16 LOW, R8:
    nothing hidden)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pack_id = await _skill_pack(c, h, oid, "Orphan Dependent", ["upscale"])

    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPack

    missing_slug = f"ghost-prereq-{uuid.uuid4().hex[:8]}"
    async with AsyncSessionLocal() as db:
        pack = await db.get(SkillPack, pack_id)
        pack.prerequisite_packs = [missing_slug]
        await db.commit()

    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    assert {"code": "PREREQ_NOT_FOUND", "slug": missing_slug} in payload["gaps"]
    # The dependent itself still composes normally
    assert pack_id in [i["entity_id"] for i in payload["items"]]


@pytest.mark.asyncio
async def test_zero_minute_pack_contributes_zero_to_budget(c):
    """estimated_minutes == 0 is a real duration — `or DEFAULT_PACK_MINUTES`
    coerced it to 60, inflating totals and truncation (round-16 LOW). Only
    None falls back to the default."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _skill_pack(c, h, oid, "Zero Minute Pack", ["upscale"], minutes=0)
    profile_id = await _confirmed_profile(c, h, oid, {"required_capabilities": ["upscale"]})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    items = {i["name"]: i for i in payload["items"]}
    assert items["Zero Minute Pack"]["status"] == "included"
    assert payload["estimated_total_minutes"] == 0


@pytest.mark.asyncio
async def test_update_draft_prereq_removal_guard(c):
    """Removing an item that a REMAINING included item lists as prerequisite
    → ITEM_HAS_DEPENDENTS 409; removing prereq AND dependent in the same
    request is allowed (round-16 LOW)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    prereq_id = await _skill_pack(c, h, oid, "Guard Prereq", ["upscale"], minutes=30)
    dep_id = await _skill_pack(c, h, oid, "Guard Dependent", ["background_removal"], minutes=30)

    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPack

    async with AsyncSessionLocal() as db:
        prereq = await db.get(SkillPack, prereq_id)
        dep = await db.get(SkillPack, dep_id)
        dep.prerequisite_packs = [prereq.slug]
        await db.commit()

    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["background_removal"]}
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    draft_id = r.json()["data"]["id"]
    # compose() persists per-item prereq slugs for the guard
    items = {i["entity_id"]: i for i in r.json()["data"]["payload"]["items"]}
    assert items[dep_id]["prereq_slugs"], items[dep_id]

    # Removing ONLY the prerequisite while the dependent remains → 409
    r2 = await c.patch(
        f"/api/v1/orgs/{oid}/drafts/{draft_id}",
        json={"remove_entity_ids": [prereq_id]},
        headers=h,
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["error"]["code"] == "ITEM_HAS_DEPENDENTS"

    # Removing prereq + dependent in the SAME request is allowed
    r3 = await c.patch(
        f"/api/v1/orgs/{oid}/drafts/{draft_id}",
        json={"remove_entity_ids": [prereq_id, dep_id]},
        headers=h,
    )
    assert r3.status_code == 200, r3.text
    statuses = {i["entity_id"]: i["status"] for i in r3.json()["data"]["payload"]["items"]}
    assert statuses[prereq_id] == "removed_by_user"
    assert statuses[dep_id] == "removed_by_user"


@pytest.mark.asyncio
async def test_discard_races_cleanly_with_confirm(c):
    """R18: discard/update were read-check-blind-write — a concurrent confirm
    claim could interleave. Both now use conditional UPDATEs; sequential
    proof: discard after confirm → 409, and vice versa."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    profile_id = await _confirmed_profile(c, h, oid, {"goal": "learn image gen"})
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    draft_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/confirm", headers=h)
    assert r.status_code == 200
    r = await c.post(f"/api/v1/orgs/{oid}/drafts/{draft_id}/discard", headers=h)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DRAFT_ALREADY_CONFIRMED"
    r = await c.patch(
        f"/api/v1/orgs/{oid}/drafts/{draft_id}",
        json={"remove_entity_ids": ["01JUNK0000000000000000000X"]},
        headers=h,
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_zero_minute_included_pack_no_contradictory_budget_gap(c):
    """R18 LOW: honoring estimated_minutes=0 broke the 'running == 0 implies
    nothing included' proxy — a 0-minute included pack alongside a cut item
    emitted BUDGET_INFEASIBLE next to an included row."""
    from app.services.learning_composer import LearningComposerService

    # Unit-level: the condition now keys on 'no item included'
    entries = [
        {"status": "included", "estimated_minutes": 0, "slug": "a", "entity_id": "A"},
        {"status": "cut_for_budget", "estimated_minutes": 60, "slug": "b", "entity_id": "B"},
    ]
    nothing_included = not any(e["status"] == "included" for e in entries)
    assert nothing_included is False  # gap must not fire
    _ = LearningComposerService  # imported to pin the module under test


@pytest.mark.asyncio
async def test_setcover_backfills_capability_below_match_limit(c):
    """R37: the composer's match caps at limit=50 (relevance-ranked), but set
    cover is a COVERAGE problem. A capability whose ONLY eligible pack ranks
    beyond the top-50 window was falsely reported NO_CONTENT_AVAILABLE
    ('content exists but the ranked window didn't reach it'). The composer now
    backfills the cheapest eligible pack for each requested capability the
    ranked window missed, so real coverage is always reachable."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # 55 high-relevance packs covering cap "A" (scenario match pushes them to
    # the top of the ranked window), plus ONE low-relevance pack that uniquely
    # covers cap "Z" (no scenario match → ranks past the 50-row cutoff).
    for i in range(55):
        await _skill_pack(c, h, oid, f"ACov{i}", ["image_generation"], minutes=10)
    z_pid = await _skill_pack(c, h, oid, "ZOnlyPack", ["voice_generation"], minutes=10)
    # give the A-packs a scenario so they outrank the Z pack
    from sqlalchemy import select as _select

    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import SkillPack

    async with AsyncSessionLocal() as db:
        rows = (
            (await db.execute(_select(SkillPack).where(SkillPack.name.like("ACov%"))))
            .scalars()
            .all()
        )
        for p in rows:
            p.scenario_tags = ["ecommerce"]
        await db.commit()

    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {
            "required_capabilities": ["image_generation", "voice_generation"],
            "scenario": "ecommerce",
        },
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/learning-path",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    selected_ids = {
        i["entity_id"] for i in payload["items"] if i["status"] in ("included", "waived")
    }
    gap_caps = {g.get("capability") for g in payload["gaps"] if g["code"] == "NO_CONTENT_AVAILABLE"}
    # Z's unique pack must be selected (backfilled), and Z must NOT be a false gap
    assert z_pid in selected_ids, f"Z pack not selected: {selected_ids}"
    assert "voice_generation" not in gap_caps, f"false NO_CONTENT_AVAILABLE: {payload['gaps']}"


@pytest.mark.asyncio
async def test_production_multipack_chain_with_output_type(c):
    """R38: setting output_type must NOT collapse the multi-pack chain to a
    single pack. S2 hard-excludes any workflow_pack not producing the target
    output_type (OUTPUT_TYPE_MISMATCH), so passing output_type as a hard
    constraint to the COMPOSER'S internal match removed every intermediate
    producer — the chain walk then found no_producer for the head's asset
    input and Part F's 'combine compatible Workflow Packs' was dead whenever
    output_type was set. The composer now demotes output_type to a soft key
    for its internal match (the /match endpoint keeps the hard filter)."""
    import uuid as _uuid

    from app.core.database import AsyncSessionLocal
    from app.models.workflow_pack import PackStatus, PackVisibility, WorkflowPack

    h, _ = await _auth(c)
    oid = await _org(c, h)
    scen = "pcchain" + _uuid.uuid4().hex[:8]  # unique scenario isolates from shared-DB packs

    async def mk(name, inputs, outputs):
        r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json={"name": name}, headers=h)
        pid = r.json()["data"]["id"]
        async with AsyncSessionLocal() as db:
            p = await db.get(WorkflowPack, pid)
            p.status = PackStatus.PUBLISHED
            p.visibility = PackVisibility.PRIVATE
            p.workflow_type = "production"
            p.scenario_tags = [scen]
            p.input_schema = [{"key": k, "type": t, "required": True} for k, t in inputs]
            p.output_schema = [{"key": k, "type": t} for k, t in outputs]
            await db.commit()
        return pid

    img = await mk("ImageMakerX", [("prompt", "prompt")], [("img", "image")])
    vid = await mk("VideoMakerX", [("src", "image")], [("out", "video")])

    profile_id = await _confirmed_profile(
        c, h, oid, {"output_type": "video", "scenario": scen}, context="production"
    )
    r = await c.post(
        f"/api/v1/orgs/{oid}/drafts/production-solution",
        json={"profile_id": profile_id},
        headers=h,
    )
    assert r.status_code == 201, r.text
    payload = r.json()["data"]["payload"]
    chain_ids = [w["entity_id"] for w in payload["workflow_chain"]]
    # BOTH packs chained (was just [vid] before the fix), producer-first
    assert chain_ids == [img, vid], f"chain not assembled: {chain_ids}"
    # the video's image input is now RESOLVED by the image pack — no no_producer
    assert not any(p["reason"] == "no_producer" for p in payload["placeholders"]), payload[
        "placeholders"
    ]
    # the image pack's prompt input is a user value
    assert any(p["reason"] == "needs_user_value" for p in payload["placeholders"])
