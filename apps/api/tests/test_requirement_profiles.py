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

    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles/from-brief/{brief_id}", headers=h
    )
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
    rp = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles/from-brief/{brief_id}", headers=h
    )
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
        extraction_meta={
            "provenance": {"time_budget": "extracted", "difficulty": "user_entered"}
        },
    )
    req = RequirementProfileService.build_match_requirement(profile)
    assert "time_budget" not in req
    assert req["_soft_time_budget"] == 60
    # user_entered fields stay hard
    assert req["difficulty"] == "beginner"
