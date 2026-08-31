"""Tests for requirement profiles — form / brief / extraction paths (ADR-012 D7)."""

import json
import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

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
    return f"rp-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "RP"},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"RP-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


# ── Form path ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_from_form(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "production",
            "structured_requirements": {
                "goal": "15s product ad",
                "scenario": "ecommerce",
                "output_type": "video",
                "required_capabilities": ["image_to_video"],
            },
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["status"] == "draft"
    assert data["structured_requirements"]["output_type"] == "video"
    # All form fields carry user_entered provenance
    prov = data["extraction_meta"]["provenance"]
    assert all(v == "user_entered" for v in prov.values())


@pytest.mark.asyncio
async def test_unknown_field_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "production", "structured_requirements": {"evil_field": "x"}},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "UNKNOWN_FIELD"


@pytest.mark.asyncio
async def test_unknown_capability_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "production",
            "structured_requirements": {"required_capabilities": ["teleportation"]},
        },
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "UNKNOWN_CAPABILITY"


# ── Brief path ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_from_brief(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    rb = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={
            "title": "Ad Campaign",
            "client_name": "Acme",
            "project_type": "ecommerce",
            "objective": "Create a 15s vertical product advertisement",
            "budget_range": "$500-1000",
        },
        headers=h,
    )
    assert rb.status_code == 201, rb.text
    brief_id = rb.json()["data"]["id"]

    r = await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/from-brief/{brief_id}", headers=h)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["source_brief_id"] == brief_id
    assert data["structured_requirements"]["scenario"] == "ecommerce"
    assert data["structured_requirements"]["cost_constraint"] == "$500-1000"
    assert data["structured_requirements"]["commercial_use"] is True
    prov = data["extraction_meta"]["provenance"]
    assert prov["scenario"] == "extracted"


# ── Extraction path (flag + mocked LLM) ───────────────────


@pytest.mark.asyncio
async def test_extract_disabled_by_default(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles/extract",
        json={"context_type": "learning", "raw_request": "I want to learn AI product photos"},
        headers=h,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "EXTRACTION_DISABLED"


@pytest.mark.asyncio
async def test_extract_with_mocked_llm(c):
    from app.core.llm import LLMResponse

    h, _ = await _auth(c)
    oid = await _org(c, h)

    llm_json = json.dumps(
        {
            "goal": "Learn AI e-commerce visuals",
            "output_type": "image",
            "difficulty": "beginner",
            "required_capabilities": ["image_generation", "made_up_capability"],
        }
    )
    mock_client = AsyncMock()
    mock_client.complete = AsyncMock(
        return_value=LLMResponse(
            content=llm_json, input_tokens=10, output_tokens=20, model="mock", provider="mock"
        )
    )
    with (
        patch("app.services.requirement_profile.settings") as mock_settings,
        patch("app.core.llm.create_llm_client", return_value=mock_client),
    ):
        mock_settings.extraction_enabled = True
        r = await c.post(
            f"/api/v1/orgs/{oid}/requirement-profiles/extract",
            json={"context_type": "learning", "raw_request": "I want AI ecommerce visuals"},
            headers=h,
        )
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    sr = data["structured_requirements"]
    assert sr["goal"] == "Learn AI e-commerce visuals"
    # Known capability kept; unknown dropped to unmatched_mentions (never invented)
    assert sr["required_capabilities"] == ["image_generation"]
    assert "made_up_capability" in data["extraction_meta"]["unmatched_mentions"]
    # Everything extracted carries extracted provenance
    assert data["extraction_meta"]["provenance"]["goal"] == "extracted"
    # Original preserved
    assert data["raw_request"] == "I want AI ecommerce visuals"


@pytest.mark.asyncio
async def test_extract_malformed_llm_twice_returns_empty(c):
    from app.core.llm import LLMResponse

    h, _ = await _auth(c)
    oid = await _org(c, h)
    mock_client = AsyncMock()
    mock_client.complete = AsyncMock(
        return_value=LLMResponse(
            content="NOT VALID JSON AT ALL",
            input_tokens=1,
            output_tokens=1,
            model="mock",
            provider="mock",
        )
    )
    with (
        patch("app.services.requirement_profile.settings") as mock_settings,
        patch("app.core.llm.create_llm_client", return_value=mock_client),
    ):
        mock_settings.extraction_enabled = True
        r = await c.post(
            f"/api/v1/orgs/{oid}/requirement-profiles/extract",
            json={"context_type": "learning", "raw_request": "teach me things"},
            headers=h,
        )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["structured_requirements"] == {}
    assert data["raw_request"] == "teach me things"
    assert data["extraction_meta"]["extraction_failed"] is True
    # Retried exactly once (2 calls total)
    assert mock_client.complete.await_count == 2


# ── Edit / confirm ────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_sets_user_entered_provenance(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    rb = await c.post(
        f"/api/v1/orgs/{oid}/briefs",
        json={
            "title": "Brief for Provenance",
            "client_name": "Client Co",
            "project_type": "ecommerce",
            "objective": "Make compelling product advertisements",
        },
        headers=h,
    )
    assert rb.status_code == 201, rb.text
    brief_id = rb.json()["data"]["id"]
    rp = await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/from-brief/{brief_id}", headers=h)
    profile_id = rp.json()["data"]["id"]

    r = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{profile_id}",
        json={"edits": {"output_type": "video", "scenario": "social_media"}},
        headers=h,
    )
    assert r.status_code == 200
    prov = r.json()["data"]["extraction_meta"]["provenance"]
    # output_type is NEW and scenario's value CHANGED → both promoted
    assert prov["output_type"] == "user_entered"
    assert prov["scenario"] == "user_entered"
    assert prov["goal"] == "extracted"  # untouched stays extracted


@pytest.mark.asyncio
async def test_confirm_then_patch_rejected(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "learn"}},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    r2 = await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=h)
    assert r2.status_code == 200
    assert r2.json()["data"]["status"] == "confirmed"

    r3 = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"goal": "changed"}},
        headers=h,
    )
    assert r3.status_code == 422
    assert r3.json()["error"]["code"] == "PROFILE_ALREADY_CONFIRMED"


# ── Provenance gating (R14 unit tests) ────────────────────


def test_hard_constraints_only_user_entered():
    from app.models.matching import RequirementProfile
    from app.services.requirement_profile import RequirementProfileService

    profile = RequirementProfile(
        org_id="o",
        structured_requirements={
            "goal": "extracted goal",
            "output_type": "video",
            "required_capabilities": ["image_to_video"],
        },
        extraction_meta={
            "provenance": {
                "goal": "extracted",
                "output_type": "user_entered",
                "required_capabilities": "extracted",
            }
        },
    )
    hard = RequirementProfileService.get_hard_constraints(profile)
    assert hard == {"output_type": "video"}
    soft = RequirementProfileService.get_soft_preferences(profile)
    assert "goal" in soft


def test_build_match_requirement_demotes_extracted_caps():
    from app.models.matching import RequirementProfile
    from app.services.requirement_profile import RequirementProfileService

    profile = RequirementProfile(
        org_id="o",
        structured_requirements={
            "required_capabilities": ["image_generation"],
            "output_type": "image",
        },
        extraction_meta={
            "provenance": {
                "required_capabilities": "extracted",
                "output_type": "extracted",
            }
        },
    )
    req = RequirementProfileService.build_match_requirement(profile)
    # Extracted required caps become preferred (soft) — never hard filters
    assert "required_capabilities" not in req
    assert req["preferred_capabilities"] == ["image_generation"]
    # Extracted output_type demoted to scoring-only key
    assert "output_type" not in req
    assert req["_soft_output_type"] == "image"


def test_build_match_requirement_keeps_confirmed_caps():
    from app.models.matching import RequirementProfile
    from app.services.requirement_profile import RequirementProfileService

    profile = RequirementProfile(
        org_id="o",
        structured_requirements={"required_capabilities": ["image_generation"]},
        extraction_meta={"provenance": {"required_capabilities": "user_entered"}},
    )
    req = RequirementProfileService.build_match_requirement(profile)
    assert req["required_capabilities"] == ["image_generation"]


# ── Isolation ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_profile_cross_org_isolation(c):
    h1, _ = await _auth(c)
    o1 = await _org(c, h1)
    r = await c.post(
        f"/api/v1/orgs/{o1}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "private"}},
        headers=h1,
    )
    pid = r.json()["data"]["id"]

    h2, _ = await _auth(c)
    o2 = await _org(c, h2)
    r2 = await c.get(f"/api/v1/orgs/{o2}/requirement-profiles/{pid}", headers=h2)
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_patch_unchanged_values_keep_extracted_provenance(c):
    """R14 audit fix: PATCHing the full object back UNCHANGED must not promote
    extracted values to user_entered (which would turn them into S2 hard
    constraints the human never actually confirmed)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)

    # Seed a profile with extracted provenance via direct DB write (mirrors
    # what extraction produces without needing the LLM flag)
    from app.core.database import AsyncSessionLocal
    from app.models.matching import RequirementContext, RequirementProfile

    async with AsyncSessionLocal() as db:
        profile = RequirementProfile(
            org_id=oid,
            context_type=RequirementContext.PRODUCTION,
            raw_request="make a product video",
            structured_requirements={
                "goal": "make a product video",
                "required_capabilities": ["image_to_video"],
            },
            extraction_meta={
                "provenance": {
                    "goal": "extracted",
                    "required_capabilities": "extracted",
                }
            },
        )
        db.add(profile)
        await db.commit()
        profile_id = profile.id

    # Round-trip the FULL object back unchanged (common UI save pattern)
    r = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{profile_id}",
        json={
            "edits": {
                "goal": "make a product video",
                "required_capabilities": ["image_to_video"],
            }
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    prov = r.json()["data"]["extraction_meta"]["provenance"]
    assert prov["goal"] == "extracted"  # unchanged → stays extracted
    assert prov["required_capabilities"] == "extracted"

    # An ACTUAL change does promote
    r2 = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{profile_id}",
        json={"edits": {"goal": "make a BETTER product video"}},
        headers=h,
    )
    prov2 = r2.json()["data"]["extraction_meta"]["provenance"]
    assert prov2["goal"] == "user_entered"
    assert prov2["required_capabilities"] == "extracted"  # untouched

    # build_match_requirement still demotes the extracted caps
    from app.services.requirement_profile import RequirementProfileService

    async with AsyncSessionLocal() as db:
        stored = await db.get(RequirementProfile, profile_id)
        requirement = RequirementProfileService.build_match_requirement(stored)
        assert "required_capabilities" not in requirement
        assert requirement.get("preferred_capabilities") == ["image_to_video"]


# ── Audit fixes (Issue #21 follow-up) ─────────────────────


@pytest.mark.asyncio
async def test_time_budget_type_validation(c):
    """Untyped time_budget values crash scoring (int<=str TypeError) —
    reject anything that isn't an int in 1..100000 (audit MEDIUM 7)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for bad in ("60", -5, 0, True, 100_001, {"m": 60}):
        r = await c.post(
            f"/api/v1/orgs/{oid}/requirement-profiles",
            json={
                "context_type": "learning",
                "structured_requirements": {"time_budget": bad},
            },
            headers=h,
        )
        assert r.status_code == 422, f"time_budget={bad!r}: {r.status_code}"
        assert r.json()["error"]["code"] == "INVALID_TIME_BUDGET"
    # Valid value passes
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "learning",
            "structured_requirements": {"time_budget": 60},
        },
        headers=h,
    )
    assert r2.status_code == 201


@pytest.mark.asyncio
async def test_nul_in_structured_requirements_rejected_as_422(c):
    """NUL / control chars inside structured_requirements (or PATCH edits)
    dicts would be stored raw into JSONB and crash asyncpg → 500. The
    recursive control-char scan must reject them as 422 (only raw_request
    was previously sanitized)."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "learning",
            "structured_requirements": {"goal": "a\x00b"},
        },
        headers=h,
    )
    assert r.status_code == 422, f"{r.status_code} {r.text[:200]}"

    # Nested values and keys are scanned too
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "learning",
            "structured_requirements": {"tool_constraints": ["ok", "bad\x00tool"]},
        },
        headers=h,
    )
    assert r2.status_code == 422

    # PATCH edits path is guarded the same way
    rp = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "clean"}},
        headers=h,
    )
    pid = rp.json()["data"]["id"]
    r3 = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"goal": "x\x00y"}},
        headers=h,
    )
    assert r3.status_code == 422


@pytest.mark.asyncio
async def test_unhashable_values_rejected_as_422(c):
    """Unhashable values (lists/dicts) in output_type / difficulty /
    capability lists must be a clean 422, never a TypeError 500."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    cases = [
        ({"output_type": ["image"]}, "INVALID_OUTPUT_TYPE"),
        ({"difficulty": ["beginner"]}, "INVALID_DIFFICULTY"),
        ({"required_capabilities": [{"x": 1}]}, "INVALID_CAPABILITIES"),
        ({"preferred_capabilities": [["nested"]]}, "INVALID_CAPABILITIES"),
    ]
    for structured, code in cases:
        r = await c.post(
            f"/api/v1/orgs/{oid}/requirement-profiles",
            json={"context_type": "learning", "structured_requirements": structured},
            headers=h,
        )
        assert r.status_code == 422, f"{structured}: {r.status_code} {r.text[:200]}"
        assert r.json()["error"]["code"] == code
    # Also reachable via PATCH edits
    rp = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "g"}},
        headers=h,
    )
    pid = rp.json()["data"]["id"]
    r2 = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"output_type": ["image"]}},
        headers=h,
    )
    assert r2.status_code == 422
    assert r2.json()["error"]["code"] == "INVALID_OUTPUT_TYPE"


@pytest.mark.asyncio
async def test_tool_constraints_type_validation(c):
    h, _ = await _auth(c)
    oid = await _org(c, h)
    for bad in ("photoshop", [1, 2], [{"t": "x"}], ["x" * 101]):
        r = await c.post(
            f"/api/v1/orgs/{oid}/requirement-profiles",
            json={
                "context_type": "learning",
                "structured_requirements": {"tool_constraints": bad},
            },
            headers=h,
        )
        assert r.status_code == 422, f"tool_constraints={bad!r}: {r.status_code}"
        assert r.json()["error"]["code"] == "INVALID_TOOL_CONSTRAINTS"
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "learning",
            "structured_requirements": {"tool_constraints": ["photoshop"]},
        },
        headers=h,
    )
    assert r2.status_code == 201


def test_build_match_requirement_demotes_extracted_time_budget():
    """Extracted time_budget must become _soft_time_budget — an LLM-
    hallucinated budget can never drive hard truncation (R14 gray zone)."""
    from app.models.matching import RequirementProfile
    from app.services.requirement_profile import RequirementProfileService

    profile = RequirementProfile(
        org_id="o",
        structured_requirements={"time_budget": 60, "difficulty": "beginner"},
        extraction_meta={"provenance": {"time_budget": "extracted", "difficulty": "user_entered"}},
    )
    req = RequirementProfileService.build_match_requirement(profile)
    assert "time_budget" not in req
    assert req["_soft_time_budget"] == 60
    # user_entered fields stay hard
    assert req["difficulty"] == "beginner"


@pytest.mark.asyncio
async def test_member_cannot_edit_or_confirm_another_members_profile(c):
    """A plain member must not edit/confirm a profile owned by another member
    — otherwise they could turn someone's unconfirmed extractions into hard
    constraints (R14-adjacent). Owner + instructors may."""
    owner_h, owner = await _auth(c)
    oid = await _org(c, owner_h)

    # Owner (an instructor by role) creates a profile owned by owner.id
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "orig"}},
        headers=owner_h,
    )
    pid = r.json()["data"]["id"]

    # A second user joins as a plain student
    student_h, student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": student["id"], "role": "student"},
        headers=owner_h,
    )

    # Student cannot edit the owner's profile
    r_edit = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"goal": "hijacked"}},
        headers=student_h,
    )
    assert r_edit.status_code == 403
    assert r_edit.json()["error"]["code"] == "PROFILE_FORBIDDEN"

    # ...nor confirm it
    r_conf = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=student_h
    )
    assert r_conf.status_code == 403

    # The owner (instructor role) still can
    r_ok = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"goal": "updated by owner"}},
        headers=owner_h,
    )
    assert r_ok.status_code == 200


@pytest.mark.asyncio
async def test_student_can_edit_own_profile(c):
    """The profile's own user may edit/confirm it even as a plain student."""
    owner_h, owner = await _auth(c)
    oid = await _org(c, owner_h)
    student_h, student = await _auth(c)
    await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": student["id"], "role": "student"},
        headers=owner_h,
    )
    # Profile created BY the student (user_id = student)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "mine"}},
        headers=student_h,
    )
    pid = r.json()["data"]["id"]
    r_edit = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        json={"edits": {"goal": "my edit"}},
        headers=student_h,
    )
    assert r_edit.status_code == 200
    r_conf = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=student_h
    )
    assert r_conf.status_code == 200


def test_normalize_extracted_sanitizes_list_items():
    """_normalize_extracted must sanitize strings INSIDE list values too —
    top-level-only sanitization let zero-width/bidi payloads through
    tool_constraints items (round-16 LOW)."""
    from app.services.requirement_profile import (
        ExtractedRequirements,
        RequirementProfileService,
    )

    # Explicit escapes: ZWSP U+200B and RLO U+202E (invisible in editors)
    extracted = ExtractedRequirements(
        goal="clean\u200bgoal",
        tool_constraints=["photo\u200bshop", "after\u202eeffects"],
    )
    svc = RequirementProfileService.__new__(RequirementProfileService)
    structured, unmatched = svc._normalize_extracted(extracted, set())

    # Top-level string sanitized (existing behavior)
    assert structured["goal"] == "cleangoal"
    # List items sanitized too: ZWSP and RLO stripped
    assert structured["tool_constraints"] == ["photoshop", "aftereffects"]
    assert unmatched == []


@pytest.mark.asyncio
async def test_profile_reads_scoped_to_owner_or_instructor(c):
    """R58: profile list + detail expose raw_request — the member's
    natural-language creative/commercial ask. A peer student must not read
    another's; instructor+ and the owner can (mirrors the write boundary)."""
    h_owner, _ = await _auth(c)
    oid = await _org(c, h_owner)
    h_a, ua = await _auth(c)
    h_b, ub = await _auth(c)
    for u in (ua, ub):
        await c.post(
            f"/api/v1/orgs/{oid}/members",
            json={"user_id": u["id"], "role": "student"},
            headers=h_owner,
        )

    # Student A creates a profile with a private raw_request
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={
            "context_type": "learning",
            "structured_requirements": {"goal": "learn video editing"},
            "raw_request": "my confidential business plan",
        },
        headers=h_a,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["data"]["id"]

    # Student B cannot list or read A's profile
    lb = await c.get(f"/api/v1/orgs/{oid}/requirement-profiles", headers=h_b)
    assert pid not in [p["id"] for p in lb.json()["data"]]
    gb = await c.get(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}", headers=h_b)
    assert gb.status_code == 404

    # A sees their own; instructor sees it too
    la = await c.get(f"/api/v1/orgs/{oid}/requirement-profiles", headers=h_a)
    assert pid in [p["id"] for p in la.json()["data"]]
    assert (
        await c.get(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}", headers=h_a)
    ).status_code == 200
    assert (
        await c.get(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}", headers=h_owner)
    ).status_code == 200
    lo = await c.get(f"/api/v1/orgs/{oid}/requirement-profiles", headers=h_owner)
    assert pid in [p["id"] for p in lo.json()["data"]]


@pytest.mark.asyncio
async def test_profile_confirm_and_edit_race_guarded(c):
    """R70d: confirm() and update_profile() both gated on a stale snapshot and
    wrote via unguarded ORM assignment. Two concurrent confirms both passed
    the 'already confirmed' read; worse, an edit racing a confirm landed
    POST-CONFIRMATION edits (with user_entered provenance promotion → S2 hard
    constraints) that nobody re-reviewed. Both writes are now status-guarded
    conditional UPDATEs (WHERE status='draft'); the loser gets a clean 422."""
    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.matching import RequirementProfile
    from app.services.requirement_profile import RequirementProfileService

    h, u = await _auth(c)
    oid = await _org(c, h)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "learn"}},
        headers=h,
    )
    assert r.status_code == 201, r.text
    pid = r.json()["data"]["id"]

    # Session A primes its identity map with the DRAFT row; session B
    # confirms and commits; A's edit then runs on the stale draft snapshot —
    # its guarded write must lose (422), never mutate a confirmed profile.
    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(RequirementProfile, pid)
        assert stale.status == "draft"

        async with AsyncSessionLocal() as db_b:
            await RequirementProfileService(db_b).confirm(
                pid, oid, acting_user_id=u["id"], is_instructor=True
            )
            await db_b.commit()

        with pytest.raises(AppError) as exc_info:
            await RequirementProfileService(db_a).update_profile(
                pid,
                oid,
                {"goal": "smuggled post-confirm edit"},
                acting_user_id=u["id"],
                is_instructor=True,
            )
        assert exc_info.value.code == "PROFILE_ALREADY_CONFIRMED"
        await db_a.rollback()

    # And a second confirm on a stale draft snapshot loses cleanly too
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"goal": "x"}},
        headers=h,
    )
    pid2 = r2.json()["data"]["id"]
    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(RequirementProfile, pid2)
        assert stale.status == "draft"
        async with AsyncSessionLocal() as db_b:
            await RequirementProfileService(db_b).confirm(
                pid2, oid, acting_user_id=u["id"], is_instructor=True
            )
            await db_b.commit()
        with pytest.raises(AppError) as exc_info:
            await RequirementProfileService(db_a).confirm(
                pid2, oid, acting_user_id=u["id"], is_instructor=True
            )
        assert exc_info.value.code == "PROFILE_ALREADY_CONFIRMED"
        await db_a.rollback()

    # Final state: goal unchanged by the losing edit
    async with AsyncSessionLocal() as db:
        p = await db.get(RequirementProfile, pid)
        assert p.status == "confirmed"
        assert p.structured_requirements.get("goal") == "learn"


@pytest.mark.asyncio
async def test_profile_nonfinite_float_rejected_not_500(c):
    """R73: stdlib json.loads (FastAPI request parsing) accepts bare NaN/
    Infinity JSON tokens → real float('nan'), which passes every str/size/
    depth/ctrl check. SQLAlchemy's default JSONB serializer (allow_nan=True)
    re-emits the literal `NaN`/`Infinity` token, which Postgres rejects with
    22P02 → DBAPIError → 500. structured_requirements / edits now screen
    non-finite floats → clean 422."""
    h, _ = await _auth(c)
    oid = await _org(c, h)
    hj = {**h, "Content-Type": "application/json"}

    # NaN in a free structured field (raw JSON NaN token)
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        content=b'{"context_type":"learning","structured_requirements":{"goal": NaN}}',
        headers=hj,
    )
    assert r.status_code == 422, f"{r.status_code}: {r.text[:150]}"

    # Infinity nested in a list
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        content=b'{"context_type":"learning","structured_requirements":{"x":[1, Infinity]}}',
        headers=hj,
    )
    assert r2.status_code == 422, r2.text[:150]

    # PATCH edits path
    pid = (
        await c.post(
            f"/api/v1/orgs/{oid}/requirement-profiles",
            json={"context_type": "learning", "structured_requirements": {"goal": "ok"}},
            headers=h,
        )
    ).json()["data"]["id"]
    r3 = await c.patch(
        f"/api/v1/orgs/{oid}/requirement-profiles/{pid}",
        content=b'{"edits":{"industry": -Infinity}}',
        headers=hj,
    )
    assert r3.status_code == 422, r3.text[:150]

    # Control: a finite number is still accepted
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "learning", "structured_requirements": {"time_budget": 120}},
        headers=h,
    )
    assert r4.status_code == 201, r4.text[:150]
