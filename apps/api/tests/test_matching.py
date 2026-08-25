"""Tests for the matching engine S1-S3 pipeline (ADR-012)."""

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
    return f"mt-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "MT"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"MT-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


def _wf_definition(capability="image_generation", output_type="image"):
    return {
        "schema_version": 1,
        "inputs": [{"key": "topic", "type": "text", "required": True}],
        "outputs": [
            {"key": "final", "type": output_type, "from_step": "gen", "from_port": "result"}
        ],
        "steps": [
            {
                "id": "gen",
                "type": "provider_action",
                "name": "Generate",
                "config": {"capability": capability},
                "inputs": [],
                "outputs": [{"port": "result", "type": output_type}],
            }
        ],
        "edges": [],
        "ui": {},
    }


async def _wf_pack(c, h, oid, name, capability="image_generation", output_type="image", scenario=None):
    body = {"name": name, "workflow_type": "production"}
    if scenario:
        body["scenario_tags"] = [scenario]
    r = await c.post(f"/api/v1/orgs/{oid}/workflow-packs", json=body, headers=h)
    pid = r.json()["data"]["id"]
    await c.put(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/definition",
        json={"definition": _wf_definition(capability, output_type)},
        headers=h,
    )
    await c.post(
        f"/api/v1/orgs/{oid}/workflow-packs/{pid}/releases", json={"version": "1.0.0"}, headers=h
    )
    return pid


async def _confirmed_profile(c, h, oid, structured, context="production"):
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": context, "structured_requirements": structured},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=h)
    return pid


async def _match(c, h, oid, profile_id, target="workflow_pack", explain=False, limit=20):
    r = await c.post(
        f"/api/v1/orgs/{oid}/match",
        json={
            "requirement_profile_id": profile_id,
            "target_entity_type": target,
            "explain": explain,
            "limit": limit,
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    return r.json()["data"]


# ── S1 eligibility ────────────────────────────────────────


@pytest.mark.asyncio
async def test_s1_excludes_other_org_private_packs(c):
    """Other orgs' private packs are INVISIBLE — not even in the excluded list."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    # Same capability as org2's own pack — would rank if it were visible
    private_pid = await _wf_pack(c, h1, o1, "Org1 Private Pack", capability="upscale")

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    own_pid = await _wf_pack(c, h2, o2, "Org2 Own Pack", capability="upscale")

    # Require a capability only these packs provide, so ranked stays small
    profile_id = await _confirmed_profile(
        c, h2, o2, {"required_capabilities": ["upscale"]}
    )
    data = await _match(c, h2, o2, profile_id, limit=50)

    ranked_ids = [r["entity_id"] for r in data["results"]]
    all_ids = ranked_ids + [e["entity_id"] for e in data["excluded"]]
    assert own_pid in ranked_ids
    assert private_pid not in all_ids


# ── S2 hard constraints ───────────────────────────────────


@pytest.mark.asyncio
async def test_s2_hard_failure_distinguishable(c):
    """Pack missing a required capability lands in excluded — NOT low-ranked."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    good = await _wf_pack(c, h, oid, "Video Pack", capability="image_to_video", output_type="video")
    bad = await _wf_pack(c, h, oid, "Image Only Pack", capability="image_generation")

    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["image_to_video"]}
    )
    data = await _match(c, h, oid, profile_id)

    ranked_ids = [r["entity_id"] for r in data["results"]]
    excluded = {e["entity_id"]: e for e in data["excluded"]}
    assert good in ranked_ids
    assert bad not in ranked_ids
    assert bad in excluded
    failure = excluded[bad]["failures"][0]
    assert failure["code"] == "CAPABILITY_MISSING"
    assert failure["capability"] == "image_to_video"


@pytest.mark.asyncio
async def test_s2_output_type_mismatch(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    img = await _wf_pack(c, h, oid, "Image Pack", output_type="image")

    profile_id = await _confirmed_profile(c, h, oid, {"output_type": "video"})
    data = await _match(c, h, oid, profile_id)
    excluded = {e["entity_id"] for e in data["excluded"]}
    assert img in excluded


# ── S3 scoring ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_s3_determinism(c):
    """Two identical runs produce identical ranked order."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for i in range(3):
        await _wf_pack(c, h, oid, f"Det Pack {i}", scenario="ecommerce" if i == 0 else None)

    profile_id = await _confirmed_profile(c, h, oid, {"scenario": "ecommerce"})
    d1 = await _match(c, h, oid, profile_id)
    d2 = await _match(c, h, oid, profile_id)
    assert [r["entity_id"] for r in d1["results"]] == [r["entity_id"] for r in d2["results"]]
    assert [r["score"] for r in d1["results"]] == [r["score"] for r in d2["results"]]


@pytest.mark.asyncio
async def test_s3_scenario_boost_and_reasons(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # background_removal keeps the candidate pool to just these two packs
    matching = await _wf_pack(
        c, h, oid, "Ecom Pack", capability="background_removal", scenario="ecommerce"
    )
    other = await _wf_pack(
        c, h, oid, "Generic Pack", capability="background_removal", scenario="short_drama"
    )

    profile_id = await _confirmed_profile(
        c, h, oid, {"scenario": "ecommerce", "required_capabilities": ["background_removal"]}
    )
    data = await _match(c, h, oid, profile_id, limit=50)
    ranked = data["results"]
    ids = [r["entity_id"] for r in ranked]
    assert ids.index(matching) < ids.index(other)

    top = next(r for r in ranked if r["entity_id"] == matching)
    reason_codes = {r["code"] for r in top["reasons"]}
    assert "SCENARIO_MATCH" in reason_codes
    assert "CAPABILITY_MATCH" in reason_codes
    # Every result has a server-computed tier
    assert all(r["tier"] in ("great", "good", "fair") for r in ranked)

    other_result = next(r for r in ranked if r["entity_id"] == other)
    gap_codes = {g["code"] for g in other_result["gaps"]}
    assert "LOW_SCENARIO_MATCH" in gap_codes


@pytest.mark.asyncio
async def test_explain_tree_sums_to_score(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _wf_pack(c, h, oid, "Explain Pack", scenario="ecommerce")
    profile_id = await _confirmed_profile(c, h, oid, {"scenario": "ecommerce"})
    data = await _match(c, h, oid, profile_id, explain=True)
    top = data["results"][0]
    tree = top["explain"]
    assert tree is not None
    child_sum = sum(d["value"] for d in tree["details"])
    assert abs(tree["value"] - child_sum) < 1e-6
    assert abs(tree["value"] - top["score"]) < 1e-3


# ── Auditability ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_match_run_persisted_with_versions(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _wf_pack(c, h, oid, "Audit Pack")
    profile_id = await _confirmed_profile(c, h, oid, {"goal": "audit"})
    data = await _match(c, h, oid, profile_id)
    assert data["engine_version"] == "1.0.0"
    assert data["config_version"] == 1

    r = await c.get(f"/api/v1/orgs/{oid}/match-runs/{data['id']}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["engine_version"] == "1.0.0"


@pytest.mark.asyncio
async def test_feedback_shown_rows_written(c):
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.matching import FeedbackEvent

    h, _ = await _auth(c)
    oid = await _org(c, h)
    await _wf_pack(c, h, oid, "Feedback Pack")
    profile_id = await _confirmed_profile(c, h, oid, {"goal": "fb"})
    data = await _match(c, h, oid, profile_id)

    async with AsyncSessionLocal() as db:
        rows_r = await db.execute(
            select(FeedbackEvent).where(
                FeedbackEvent.match_run_id == data["id"],
                FeedbackEvent.event_type == "shown",
            )
        )
        rows = list(rows_r.scalars().all())
    assert len(rows) == len(data["results"])
    # R17: rank_position always present on impressions
    assert all(row.rank_position is not None for row in rows)


@pytest.mark.asyncio
async def test_feedback_event_endpoint(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    pid = await _wf_pack(c, h, oid, "FB Endpoint Pack")
    r = await c.post(
        f"/api/v1/orgs/{oid}/feedback-events",
        json={
            "entity_type": "workflow_pack",
            "entity_id": pid,
            "event_type": "opened",
            "rank_position": 1,
        },
        headers=h,
    )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_feedback_event_bounds_rejected_as_422(c):
    """Over-length entity_id (varchar(26) column) and out-of-range / negative
    rank_position must be clean 422s — never asyncpg truncation/overflow 500s,
    and never negative ranks polluting the position-bias dataset (R17)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    base = {"entity_type": "workflow_pack", "event_type": "opened"}
    bad_bodies = [
        {**base, "entity_id": "x" * 40},  # 40 chars > varchar(26)
        {**base, "entity_id": ""},  # empty
        {**base, "entity_id": "01AAAAAAAAAAAAAAAAAAAAAAAA", "rank_position": -1},
        {**base, "entity_id": "01AAAAAAAAAAAAAAAAAAAAAAAA", "rank_position": 2**40},
        {**base, "entity_id": "01AAAAAAAAAAAAAAAAAAAAAAAA", "match_run_id": "m" * 40},
    ]
    for body in bad_bodies:
        r = await c.post(f"/api/v1/orgs/{oid}/feedback-events", json=body, headers=h)
        assert r.status_code == 422, f"{body}: {r.status_code} {r.text[:200]}"


# ── Guards ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_match_unconfirmed_profile_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "production", "structured_requirements": {"goal": "x"}},
        headers=h,
    )
    profile_id = r.json()["data"]["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/match",
        json={"requirement_profile_id": profile_id, "target_entity_type": "workflow_pack"},
        headers=h,
    )
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "PROFILE_NOT_CONFIRMED"


@pytest.mark.asyncio
async def test_match_cross_org_profile_rejected(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    profile_id = await _confirmed_profile(c, h1, o1, {"goal": "private"})

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r = await c.post(
        f"/api/v1/orgs/{o2}/match",
        json={"requirement_profile_id": profile_id, "target_entity_type": "workflow_pack"},
        headers=h2,
    )
    assert r.status_code == 404


# ── Creator matching basics ───────────────────────────────


@pytest.mark.asyncio
async def test_creator_matching_requires_verified_evidence(c):
    """Creators without evidence for required caps are excluded, not low-ranked.

    Deterministic ranking + reason-provenance: A (3 strong verified rows →
    capability_evidence 0.75, above reason_min 0.7) MUST outrank W (1 weak
    row → 0.4), and A's reasons MUST carry the verified evidence chip — the
    old `any(...) or top['score'] is not None` disjunction was always True."""
    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence

    h_owner, u_owner = await _auth(c)
    oid = await _org(c, h_owner)
    h_a, u_a = await _auth(c)
    h_b, u_b = await _auth(c)
    h_w, u_w = await _auth(c)
    for u in (u_a, u_b, u_w):
        await c.post(
            f"/api/v1/orgs/{oid}/members",
            json={"user_id": u["id"], "role": "student"},
            headers=h_owner,
        )

    async with AsyncSessionLocal() as db:
        # Creator A: 3 verified rows at 100 → Bayesian-shrunk
        # capability_evidence = (3/6)*1.0 + (3/6)*0.5 = 0.75 ≥ reason_min 0.7
        for i in range(3):
            db.add(
                CreatorCapabilityEvidence(
                    org_id=oid,
                    user_id=u_a["id"],
                    capability_key="image_generation",
                    evidence_type="skill_completed",
                    evidence_id=f"01TESTEVIDENCE00000000000{i + 1}",
                    weight=1.0,
                    score=100,
                    occurred_at=datetime.now(UTC),
                )
            )
        # Creator W: 1 weak row at 10 → (1/4)*0.1 + (3/4)*0.5 = 0.4 — survives
        # S2 (has evidence) but must rank strictly below A
        db.add(
            CreatorCapabilityEvidence(
                org_id=oid,
                user_id=u_w["id"],
                capability_key="image_generation",
                evidence_type="skill_completed",
                evidence_id="01TESTEVIDENCE0000000000W1",
                weight=1.0,
                score=10,
                occurred_at=datetime.now(UTC),
            )
        )
        await db.commit()

    profile_id = await _confirmed_profile(
        c, h_owner, oid, {"required_capabilities": ["image_generation"]}, context="commercial_project"
    )
    data = await _match(c, h_owner, oid, profile_id, target="creator")

    ranked_ids = [r["entity_id"] for r in data["results"]]
    excluded_ids = {e["entity_id"] for e in data["excluded"]}
    assert u_a["id"] in ranked_ids
    assert u_w["id"] in ranked_ids
    assert u_b["id"] in excluded_ids
    # Strong verified evidence MUST outrank weak evidence (0.45-weight signal
    # difference 0.1575 dwarfs any recency jitter between fresh accounts)
    assert ranked_ids.index(u_a["id"]) < ranked_ids.index(u_w["id"])
    # Verified evidence appears as a reason chip for A — code AND provenance
    top = next(r for r in data["results"] if r["entity_id"] == u_a["id"])
    assert any(
        rs["code"] == "CAPABILITY_EVIDENCE" and rs["evidence"] == "verified"
        for rs in top["reasons"]
    ), top["reasons"]


@pytest.mark.asyncio
async def test_feedback_foreign_match_run_rejected(c):
    """Feedback rows cannot be attached to another org's match run
    (audit LOW 5 — loose non-FK ref needs an ownership check)."""
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    await _wf_pack(c, h1, o1, "FB Cross Pack", capability="upscale")
    profile_id = await _confirmed_profile(c, h1, o1, {"required_capabilities": ["upscale"]})
    data = await _match(c, h1, o1, profile_id)
    run_id = data["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r = await c.post(
        f"/api/v1/orgs/{o2}/feedback-events",
        json={
            "match_run_id": run_id,
            "entity_type": "workflow_pack",
            "entity_id": "01AAAAAAAAAAAAAAAAAAAAAAAA",
            "event_type": "opened",
        },
        headers=h2,
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "MATCH_RUN_NOT_FOUND"

    # Own org with the same run id still works
    r2 = await c.post(
        f"/api/v1/orgs/{o1}/feedback-events",
        json={
            "match_run_id": run_id,
            "entity_type": "workflow_pack",
            "entity_id": "01AAAAAAAAAAAAAAAAAAAAAAAA",
            "event_type": "opened",
        },
        headers=h1,
    )
    assert r2.status_code == 201


# ── Audit fixes (Issue #21 follow-up) ─────────────────────


@pytest.mark.asyncio
async def test_s2_preferred_only_skill_pack_survives(c):
    """A skill pack teaching only a PREFERRED capability must survive S2 —
    the composer's set cover assembles coverage over required AND preferred
    caps (audit MEDIUM 5)."""
    from app.core.database import AsyncSessionLocal
    from app.models.skill_pack import PackStatus, SkillPack

    h, _ = await _auth(c)
    oid = await _org(c, h)

    async def _sp(name, caps):
        r = await c.post(
            f"/api/v1/orgs/{oid}/packs",
            json={"name": name, "summary": "s"},
            headers=h,
        )
        pid = r.json()["data"]["id"]
        async with AsyncSessionLocal() as db:
            pack = await db.get(SkillPack, pid)
            pack.capability_tags = caps
            pack.status = PackStatus.PUBLISHED
            await db.commit()
        return pid

    preferred_only = await _sp("Preferred Only", ["upscale"])
    irrelevant = await _sp("Irrelevant", ["text_to_speech"])

    profile_id = await _confirmed_profile(
        c,
        h,
        oid,
        {
            "required_capabilities": ["image_generation"],
            "preferred_capabilities": ["upscale"],
        },
        context="learning",
    )
    data = await _match(c, h, oid, profile_id, target="skill_pack", limit=50)
    ranked_ids = [r["entity_id"] for r in data["results"]]
    excluded_ids = {e["entity_id"] for e in data["excluded"]}
    assert preferred_only in ranked_ids
    assert irrelevant not in ranked_ids
    if irrelevant in excluded_ids:
        failures = next(
            e for e in data["excluded"] if e["entity_id"] == irrelevant
        )["failures"]
        assert failures[0]["code"] == "CAPABILITY_IRRELEVANT"


@pytest.mark.asyncio
async def test_excluded_rows_capped_at_50(c):
    """Persisted/returned hard-failure rows are capped; excluded_count keeps
    the true total (audit MEDIUM — match_results bloat)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    # One matching pack; the shared registry supplies plenty of non-matching
    # public packs from other tests, all excluded on CAPABILITY_MISSING.
    good = await _wf_pack(c, h, oid, "Cap Match", capability="image_to_video", output_type="video")
    profile_id = await _confirmed_profile(
        c, h, oid, {"required_capabilities": ["image_to_video"]}
    )
    data = await _match(c, h, oid, profile_id, limit=50)
    assert good in [r["entity_id"] for r in data["results"]]
    assert len(data["excluded"]) <= 50
    # The run-level counter is never capped
    assert data["excluded_count"] >= len(data["excluded"])


def test_soft_keys_feed_scoring_signals():
    """_soft_output_type/_soft_difficulty must influence scoring — the R14
    demotion strips them from S2 hard filters but scoring should still use
    them (audit LOW: 'keep for scoring' comment was dead code)."""
    from types import SimpleNamespace

    from app.services.matching.scoring import _entity_signals

    spec = SimpleNamespace(target_entity_type="workflow_pack")
    entity = SimpleNamespace(
        capability_tags=["image_generation"],
        scenario_tags=[],
        tool_tags=[],
        output_schema=[{"key": "img", "type": "image"}],
        install_count=0,
        created_at=None,
    )
    # Soft output_type matching the entity should score 1.0, not neutral 0.5
    soft = _entity_signals(entity, spec, {"_soft_output_type": "image"})
    hard = _entity_signals(entity, spec, {"output_type": "image"})
    assert soft["output_type_match"] == hard["output_type_match"] == 1.0
    # And a mismatching soft type scores 0.0 (used, not ignored)
    miss = _entity_signals(entity, spec, {"_soft_output_type": "video"})
    assert miss["output_type_match"] == 0.0


def test_soft_difficulty_feeds_skill_pack_scoring():
    from types import SimpleNamespace

    from app.services.matching.scoring import _entity_signals

    spec = SimpleNamespace(target_entity_type="skill_pack")
    entity = SimpleNamespace(
        capability_tags=["upscale"],
        scenario_tags=[],
        difficulty="beginner",
        estimated_minutes=30,
        install_count=0,
    )
    soft = _entity_signals(entity, spec, {"_soft_difficulty": "beginner"})
    hard = _entity_signals(entity, spec, {"difficulty": "beginner"})
    assert soft["difficulty_fit"] == hard["difficulty_fit"]


def test_skill_pack_teach_match_uses_soft_and_preferred_caps():
    """R14 demotes extracted required caps to preferred/_soft — the skill_pack
    capability_teach_match signal must fold those keys in, or it degenerates
    to a constant 1.0 for every survivor in the common extraction flow
    (0.35-weight signal + false 'Teaches the required capabilities' chip)."""
    from types import SimpleNamespace

    from app.services.matching.scoring import _entity_signals

    spec = SimpleNamespace(target_entity_type="skill_pack")

    def _pack(caps):
        return SimpleNamespace(
            capability_tags=caps,
            scenario_tags=[],
            difficulty="beginner",
            estimated_minutes=30,
            install_count=0,
        )

    teaching = _pack(["image_generation"])
    not_teaching = _pack(["text_to_speech"])

    for requirement in (
        {"_soft_required_capabilities": ["image_generation"]},
        {"preferred_capabilities": ["image_generation"]},  # R14 demotion target
    ):
        s_teach = _entity_signals(teaching, spec, requirement)
        s_miss = _entity_signals(not_teaching, spec, requirement)
        # Signal must DISCRIMINATE — not constant 1.0 for both
        assert s_teach["capability_teach_match"] == 1.0, requirement
        assert s_miss["capability_teach_match"] == 0.0, requirement
