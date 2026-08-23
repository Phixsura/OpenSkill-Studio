"""Tests for creator matching + assignment offers (ADR-013, Issue #21 Part G)."""

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
    return f"crm-{uuid.uuid4().hex[:8]}@test.com"


async def _auth(c, name="Crm"):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": name},
    )
    d = r.json()
    return {"Authorization": f"Bearer {d['access_token']}"}, d["user"]


async def _org(c, h):
    r = await c.post("/api/v1/orgs", json={"name": f"G-{uuid.uuid4().hex[:8]}"}, headers=h)
    return r.json()["data"]["id"]


async def _add_member(c, h_owner, oid, user, role="student"):
    r = await c.post(
        f"/api/v1/orgs/{oid}/members",
        json={"user_id": user["id"], "role": role},
        headers=h_owner,
    )
    assert r.status_code in (200, 201), r.text


async def _completed_skill(c, h, oid, user_id, tag="image_generation"):
    """Create an org skill tagged with a capability + a COMPLETED progress row."""
    cat = (
        await c.post(
            f"/api/v1/orgs/{oid}/categories",
            json={"name": f"Cat-{uuid.uuid4().hex[:4]}"},
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/skills",
        json={
            "name": f"Skill-{uuid.uuid4().hex[:4]}",
            "description": "d" * 10,
            "difficulty": "beginner",
            "category_id": cat,
            "tags": [tag],
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    skill_id = r.json()["data"]["id"]

    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.models.skill import ProgressStatus, SkillProgress

    async with AsyncSessionLocal() as db:
        db.add(
            SkillProgress(
                org_id=oid,
                skill_id=skill_id,
                user_id=user_id,
                status=ProgressStatus.COMPLETED,
                exercises_total=1,
                exercises_done=1,
                best_score=90,
                completed_at=datetime.now(UTC),
            )
        )
        await db.commit()
    return skill_id


async def _project(c, h, oid):
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": f"Proj-{uuid.uuid4().hex[:4]}",
            "description": "A commercial project needing a creator",
            "instructions": "Deliver the assets described in the brief",
            "rubric": [{"criterion": "Quality", "max_score": 100}],
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    return r.json()["data"]["id"]


async def _confirmed_profile(c, h, oid, structured):
    r = await c.post(
        f"/api/v1/orgs/{oid}/requirement-profiles",
        json={"context_type": "talent_matching", "structured_requirements": structured},
        headers=h,
    )
    pid = r.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{oid}/requirement-profiles/{pid}/confirm", headers=h)
    return pid


# ── Evidence derivation ───────────────────────────────────


@pytest.mark.asyncio
async def test_rebuild_evidence_from_skill_progress(c):
    h, owner = await _auth(c)
    oid = await _org(c, h)
    await _completed_skill(c, h, oid, owner["id"], tag="image_generation")

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        svc = CreatorMatchingService(db)
        count = await svc.rebuild_evidence(oid, owner["id"])
        await db.commit()
        assert count >= 1
        ev_r = await db.execute(
            select(CreatorCapabilityEvidence).where(
                CreatorCapabilityEvidence.org_id == oid,
                CreatorCapabilityEvidence.user_id == owner["id"],
            )
        )
        rows = list(ev_r.scalars().all())
        assert any(
            r.capability_key == "image_generation" and r.evidence_type == "skill_completed"
            for r in rows
        )
        # Idempotent: rebuild again → same count, no duplicates
        count2 = await svc.rebuild_evidence(oid, owner["id"])
        await db.commit()
        assert count2 == count


# ── Shortlist ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_shortlist_ranks_evidence_and_excludes_unverified(c):
    h_owner, owner = await _auth(c, "Owner")
    oid = await _org(c, h_owner)

    h_skilled, skilled = await _auth(c, "Skilled Creator")
    h_unskilled, unskilled = await _auth(c, "Unskilled Creator")
    await _add_member(c, h_owner, oid, skilled)
    await _add_member(c, h_owner, oid, unskilled)
    await _completed_skill(c, h_owner, oid, skilled["id"], tag="image_generation")

    project_id = await _project(c, h_owner, oid)
    profile_id = await _confirmed_profile(
        c, h_owner, oid, {"required_capabilities": ["image_generation"]}
    )

    r = await c.get(
        f"/api/v1/orgs/{oid}/projects/{project_id}/creator-shortlist?profile_id={profile_id}",
        headers=h_owner,
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    ranked_ids = [x["entity_id"] for x in data["results"]]
    excluded_ids = [x["entity_id"] for x in data["excluded"]]

    assert skilled["id"] in ranked_ids
    # Unverified member is EXCLUDED (hard constraint), not just ranked low
    assert unskilled["id"] in excluded_ids
    assert unskilled["id"] not in ranked_ids

    # Evidence detail attached, grouped by capability
    skilled_entry = next(x for x in data["results"] if x["entity_id"] == skilled["id"])
    assert "image_generation" in skilled_entry["evidence"]
    assert skilled_entry["evidence"]["image_generation"][0]["evidence_type"] == "skill_completed"

    # NO auto-assignment: shortlisting created zero assignment rows
    r2 = await c.get(f"/api/v1/orgs/{oid}/creator-assignments", headers=h_owner)
    assert r2.json()["data"] == []

    _ = h_skilled, h_unskilled


# ── Assignment offers ─────────────────────────────────────


@pytest.mark.asyncio
async def test_offer_accept_flow(c):
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Creator")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)

    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    assert r.status_code == 201, r.text
    assignment = r.json()["data"]
    assert assignment["status"] == "offered"
    assert assignment["assigned_by"] is not None  # human assigner recorded

    # Creator accepts
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{assignment['id']}/respond",
        json={"accept": True},
        headers=h_creator,
    )
    assert r2.status_code == 200
    assert r2.json()["data"]["status"] == "accepted"
    assert r2.json()["data"]["responded_at"] is not None

    # Double respond → 409
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{assignment['id']}/respond",
        json={"accept": False},
        headers=h_creator,
    )
    assert r3.status_code == 409


@pytest.mark.asyncio
async def test_offer_decline(c):
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Decliner")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    aid = r.json()["data"]["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": False},
        headers=h_creator,
    )
    assert r2.json()["data"]["status"] == "declined"


@pytest.mark.asyncio
async def test_non_offered_user_cannot_respond(c):
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Target")
    h_other, other = await _auth(c, "Bystander")
    await _add_member(c, h_owner, oid, creator)
    await _add_member(c, h_owner, oid, other)
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    aid = r.json()["data"]["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": True},
        headers=h_other,
    )
    assert r2.status_code == 403
    assert r2.json()["error"]["code"] == "NOT_YOUR_ASSIGNMENT"
    _ = h_creator


@pytest.mark.asyncio
async def test_duplicate_offer_rejected(c):
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    _h_creator, creator = await _auth(c, "Dup Target")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)
    body = {"project_id": project_id, "user_id": creator["id"]}
    r1 = await c.post(f"/api/v1/orgs/{oid}/creator-assignments", json=body, headers=h_owner)
    assert r1.status_code == 201
    r2 = await c.post(f"/api/v1/orgs/{oid}/creator-assignments", json=body, headers=h_owner)
    assert r2.status_code == 409
    assert r2.json()["error"]["code"] == "ASSIGNMENT_EXISTS"


@pytest.mark.asyncio
async def test_offer_to_non_member_rejected(c):
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    _h_out, outsider = await _auth(c, "Outsider")
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": outsider["id"]},
        headers=h_owner,
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "NOT_A_MEMBER"


@pytest.mark.asyncio
async def test_student_cannot_offer_assignments(c):
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_student, student = await _auth(c, "Student")
    await _add_member(c, h_owner, oid, student)
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": student["id"]},
        headers=h_student,
    )
    assert r.status_code == 403
