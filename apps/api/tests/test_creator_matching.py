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
    assert r3.json()["error"]["code"] == "ASSIGNMENT_ALREADY_RESPONDED"


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


@pytest.mark.asyncio
async def test_evidence_scores_stored_on_100_scale(c):
    """Evidence scores are stored 0-100; scoring.py normalizes ONCE at read
    time. best_score is a SUM across exercises, so rebuild_evidence must
    divide by the exercise count — and the read-time check must CALL the
    real _creator_signals, not re-implement its formula on test constants."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    skill_id = await _completed_skill(c, h, oid, owner["id"], tag="image_generation")

    # Seed 2 exercises for the skill and bump best_score to a SUM of 150
    # (2 exercises at 75 each) — the stored evidence score must be the
    # per-exercise normalization 150/2 = 75, NOT a clamped 100.
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.models.skill import Exercise, ExerciseType, SkillProgress
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        for i in range(2):
            db.add(
                Exercise(
                    org_id=oid,
                    skill_id=skill_id,
                    title=f"Ex {i}",
                    description="d" * 10,
                    type=ExerciseType.TEXT_ANSWER,
                    config={},
                    sort_order=i,
                )
            )
        sp_r = await db.execute(
            select(SkillProgress).where(
                SkillProgress.skill_id == skill_id,
                SkillProgress.user_id == owner["id"],
            )
        )
        progress = sp_r.scalar_one()
        progress.best_score = 150  # SUM across the 2 exercises
        await db.commit()

    async with AsyncSessionLocal() as db:
        svc = CreatorMatchingService(db)
        await svc.rebuild_evidence(oid, owner["id"])
        await db.commit()
        ev_r = await db.execute(
            select(CreatorCapabilityEvidence).where(
                CreatorCapabilityEvidence.org_id == oid,
                CreatorCapabilityEvidence.user_id == owner["id"],
                CreatorCapabilityEvidence.evidence_type == "skill_completed",
            )
        )
        row = ev_r.scalars().first()
        assert row is not None
        # 150 summed over 2 exercises → 75 on the 0-100 scale
        assert float(row.score) == 75.0

        # Read-time normalization through the REAL scoring path: one evidence
        # row scored 75 → base 0.75, Bayesian shrinkage with n=1 →
        # (1/4)*0.75 + (3/4)*0.5 = 0.5625. Fails if scoring.py's formula
        # changes (unlike the old inline re-implementation).
        from types import SimpleNamespace

        from app.services.matching.scoring import _creator_signals

        spec = SimpleNamespace(org_id=oid, target_entity_type="creator")
        signal_rows = await _creator_signals(
            db,
            [{"id": owner["id"], "last_login_at": None}],
            spec,
            {"required_capabilities": ["image_generation"]},
        )
        assert len(signal_rows) == 1
        _, signals = signal_rows[0]
        assert signals["capability_evidence"] == pytest.approx(0.5625)


@pytest.mark.asyncio
async def test_shortlist_evidence_staleness_gate(c):
    """rebuild_org_evidence skips when evidence is fresh (<10 min) unless
    forced (audit HIGH 2 — no mass rewrite per shortlist request). Sequential
    rebuilds must be idempotent: the advisory-lock + post-lock staleness
    re-check means the row count never grows (no duplicated evidence)."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    await _completed_skill(c, h, oid, owner["id"], tag="image_generation")

    from sqlalchemy import func as sa_func
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async def _count(db):
        r = await db.execute(
            select(sa_func.count(CreatorCapabilityEvidence.id)).where(
                CreatorCapabilityEvidence.org_id == oid
            )
        )
        return r.scalar_one()

    async with AsyncSessionLocal() as db:
        svc = CreatorMatchingService(db)
        first = await svc.rebuild_org_evidence(oid)
        await db.commit()
        assert first >= 1
        count_after_first = await _count(db)
        # Fresh evidence → gated rebuild is a no-op
        second = await svc.rebuild_org_evidence(oid)
        assert second == 0
        await db.commit()
        assert await _count(db) == count_after_first  # no duplicates
        # force=True bypasses the gate — still idempotent (delete + re-insert)
        third = await svc.rebuild_org_evidence(oid, force=True)
        await db.commit()
        assert third == first
        assert await _count(db) == count_after_first


@pytest.mark.asyncio
async def test_accept_offer_for_archived_project_rejected(c):
    """Open offers survive project archival (soft delete) — accepting must be
    blocked with PROJECT_NOT_AVAILABLE 409, never a silent accept against a
    dead project. Declining stays allowed (cleans up the zombie offer)."""
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Archived Target")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    assert r.status_code == 201, r.text
    aid = r.json()["data"]["id"]

    # Archive the project underneath the open offer (direct DB update — the
    # delete endpoint soft-deletes to ARCHIVED the same way)
    from app.core.database import AsyncSessionLocal
    from app.models.project import Project
    from app.models.skill import ContentStatus

    async with AsyncSessionLocal() as db:
        project = await db.get(Project, project_id)
        project.status = ContentStatus.ARCHIVED
        await db.commit()

    r2 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": True},
        headers=h_creator,
    )
    assert r2.status_code == 409, r2.text
    assert r2.json()["error"]["code"] == "PROJECT_NOT_AVAILABLE"

    # Declining the zombie offer still works
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": False},
        headers=h_creator,
    )
    assert r3.status_code == 200
    assert r3.json()["data"]["status"] == "declined"


def test_assignment_response_tolerates_null_assigned_by():
    """creator_assignments.assigned_by is nullable with ON DELETE SET NULL —
    the response schema must validate a row whose assigner was deleted, or
    every assignments endpoint 500s for the whole org."""
    from datetime import UTC, datetime

    from app.models.composer import CreatorAssignment
    from app.schemas.composer import AssignmentResponse

    assignment = CreatorAssignment(
        id="01AAAAAAAAAAAAAAAAAAAAAAAA",
        org_id="01BBBBBBBBBBBBBBBBBBBBBBBB",
        project_id="01CCCCCCCCCCCCCCCCCCCCCCCC",
        user_id="01DDDDDDDDDDDDDDDDDDDDDDDD",
        status="offered",
        assigned_by=None,  # assigner deleted → SET NULL fired
        created_at=datetime.now(UTC),
    )
    resp = AssignmentResponse.model_validate(assignment)
    assert resp.assigned_by is None


@pytest.mark.asyncio
async def test_offer_rejects_foreign_and_overlong_match_run(c):
    """offer_assignment must validate the loose match_run_id ref the same way
    feedback-events does: a cross-org run → 404, an over-length id → 422 (not
    a StringDataRightTruncation 500)."""
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Creator")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)

    # A match run owned by a DIFFERENT org
    h_other, _ = await _auth(c, "Other")
    o2 = await _org(c, h_other)
    prof2 = await c.post(
        f"/api/v1/orgs/{o2}/requirement-profiles",
        json={"context_type": "commercial_project", "structured_requirements": {"goal": "x"}},
        headers=h_other,
    )
    p2 = prof2.json()["data"]["id"]
    await c.post(f"/api/v1/orgs/{o2}/requirement-profiles/{p2}/confirm", headers=h_other)
    mr = await c.post(
        f"/api/v1/orgs/{o2}/match",
        json={"requirement_profile_id": p2, "target_entity_type": "creator"},
        headers=h_other,
    )
    foreign_run_id = mr.json()["data"]["id"]

    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"], "match_run_id": foreign_run_id},
        headers=h_owner,
    )
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "MATCH_RUN_NOT_FOUND"

    # Over-length match_run_id → clean 422, never a 500
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"], "match_run_id": "x" * 200},
        headers=h_owner,
    )
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_respond_race_loser_gets_409_not_double_write(c):
    """The read-check-write in respond_assignment is guarded by a conditional
    UPDATE (WHERE status='offered'): a session whose pre-read saw 'offered'
    but whose UPDATE lands after another response must get
    ASSIGNMENT_ALREADY_RESPONDED 409 — never silently overwrite the first
    response (round-16 LOW)."""
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    _h_creator, creator = await _auth(c, "Race Target")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    aid = r.json()["data"]["id"]

    from app.core.database import AsyncSessionLocal
    from app.exceptions import AppError
    from app.models.composer import CreatorAssignment
    from app.services.creator_matching import CreatorMatchingService

    # Session A loads the offer while it is still 'offered' (stale read)
    async with AsyncSessionLocal() as db_a:
        stale = await db_a.get(CreatorAssignment, aid)
        assert stale.status == "offered"

        # Session B wins the race: declines and commits first
        async with AsyncSessionLocal() as db_b:
            await CreatorMatchingService(db_b).respond_assignment(
                aid, oid, creator["id"], accept=False
            )
            await db_b.commit()

        # Session A's pre-read still says 'offered' (identity map) — the
        # status-guarded UPDATE must catch the lost race with a clean 409
        with pytest.raises(AppError) as exc:
            await CreatorMatchingService(db_a).respond_assignment(
                aid, oid, creator["id"], accept=True
            )
        assert exc.value.code == "ASSIGNMENT_ALREADY_RESPONDED"
        assert exc.value.status_code == 409

    # The first response (declined) is what persisted
    async with AsyncSessionLocal() as db:
        final = await db.get(CreatorAssignment, aid)
        assert final.status == "declined"


# ── R39: project→capability resolution for evidence sources 3/4/6 ──
# project.project_type is restricted to {general, ai_visual} (schemas/project
# VALID_PROJECT_TYPES) which shares no member with capability keys — deriving
# capability from it alone made approved_submission and eval_result evidence
# structurally dead. Capability must resolve via the linked brief or the
# confirmed production draft that materialized the project.


async def _seed_project_with_brief(c, h, oid, brief_project_type):
    """Brief (free-text project_type) → converted project (client_brief_id set)."""
    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": f"Brief-{uuid.uuid4().hex[:4]}",
                "client_name": "Client",
                "project_type": brief_project_type,
                "objective": "Deliver production-grade generated imagery",
            },
            headers=h,
        )
    ).json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/convert",
        json={"rubric": [{"criterion": "Overall", "max_score": 100}]},
        headers=h,
    )
    assert r.status_code == 201, r.text
    return r.json()["data"]["id"], bid


async def _seed_approved_review(oid, project_id, user_id, score=80):
    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.models.project import (
        ReviewerType,
        ReviewStatus,
        Submission,
        SubmissionReview,
        SubmissionStatus,
    )

    async with AsyncSessionLocal() as db:
        sub = Submission(
            org_id=oid,
            project_id=project_id,
            user_id=user_id,
            status=SubmissionStatus.APPROVED,
            submitted_at=datetime.now(UTC),
        )
        db.add(sub)
        await db.flush()
        review = SubmissionReview(
            submission_id=sub.id,
            reviewer_type=ReviewerType.INSTRUCTOR,
            status=ReviewStatus.APPROVED,
            score=score,
        )
        db.add(review)
        await db.commit()
        return sub.id


@pytest.mark.asyncio
async def test_approved_submission_evidence_via_brief_project(c):
    """Approved review on a brief-converted project attests the brief's
    capability (project.project_type='ai_visual' alone never matches)."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    project_id, _ = await _seed_project_with_brief(c, h, oid, "image_generation")
    await _seed_approved_review(oid, project_id, owner["id"], score=80)

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, owner["id"])
        await db.commit()
        rows = list(
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.org_id == oid,
                        CreatorCapabilityEvidence.user_id == owner["id"],
                        CreatorCapabilityEvidence.evidence_type == "approved_submission",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1, [r.capability_key for r in rows]
        assert rows[0].capability_key == "image_generation"
        # Review score 80 on a max_score-100 project → stored as 80.0
        assert float(rows[0].score) == pytest.approx(80.0)


@pytest.mark.asyncio
async def test_eval_result_evidence_via_confirmed_production_draft(c):
    """COMPLETED eval on a project materialized from a confirmed production
    draft attests the draft's required_capabilities."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    project_id = await _project(c, h, oid)  # project_type=general, no brief

    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.models.composer import SolutionDraft
    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask
    from app.models.project import Submission, SubmissionStatus

    async with AsyncSessionLocal() as db:
        db.add(
            SolutionDraft(
                org_id=oid,
                draft_type="production_solution",
                payload={
                    "required_capabilities": [
                        {"capability": "image_to_video", "features": []},
                        {"capability": "voice_generation", "features": []},
                    ]
                },
                engine_version="1.0.0",
                status="confirmed",
                materialized_entity_id=project_id,
                created_by=owner["id"],
            )
        )
        sub = Submission(
            org_id=oid,
            project_id=project_id,
            user_id=owner["id"],
            status=SubmissionStatus.APPROVED,
            submitted_at=datetime.now(UTC),
        )
        db.add(sub)
        await db.flush()
        db.add(
            EvaluationTask(
                org_id=oid,
                submission_id=sub.id,
                type=EvalType.SUBMISSION_REVIEW,
                status=EvalStatus.COMPLETED,
                config={},
                # Real EvaluationService shape: total_score/max_score
                result={"total_score": 91, "max_score": 100, "scores": []},
                completed_at=datetime.now(UTC),
            )
        )
        await db.commit()

    from sqlalchemy import select

    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, owner["id"])
        await db.commit()
        rows = list(
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.org_id == oid,
                        CreatorCapabilityEvidence.user_id == owner["id"],
                        CreatorCapabilityEvidence.evidence_type == "eval_result",
                    )
                )
            )
            .scalars()
            .all()
        )
        caps = sorted(r.capability_key for r in rows)
        assert caps == ["image_to_video", "voice_generation"], caps
        assert all(float(r.score) == pytest.approx(91.0) for r in rows)


@pytest.mark.asyncio
async def test_commercial_project_evidence_normalizes_free_text(c):
    """'Image Generation' typed in a brief's free-text project_type attests
    image_generation (snake-case normalization, not bare lowercasing)."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    creator_h, creator = await _auth(c, name="FreeText")
    await _add_member(c, h, oid, creator)

    bid = (
        await c.post(
            f"/api/v1/orgs/{oid}/briefs",
            json={
                "title": "Campaign visuals",
                "client_name": "Client",
                "project_type": "Image Generation",
                "objective": "Deliver campaign hero imagery for the brand",
            },
            headers=h,
        )
    ).json()["data"]["id"]
    # open → apply → accept
    r = await c.put(f"/api/v1/orgs/{oid}/briefs/{bid}", json={"status": "open"}, headers=h)
    assert r.status_code == 200, r.text
    r = await c.post(
        f"/api/v1/orgs/{oid}/briefs/{bid}/apply",
        json={"note": "I can deliver this"},
        headers=creator_h,
    )
    assert r.status_code == 201, r.text
    app_id = r.json()["data"]["id"]
    r = await c.put(
        f"/api/v1/orgs/{oid}/briefs/{bid}/applications/{app_id}",
        json={"status": "accepted"},
        headers=h,
    )
    assert r.status_code == 200, r.text

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, creator["id"])
        await db.commit()
        rows = list(
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.org_id == oid,
                        CreatorCapabilityEvidence.user_id == creator["id"],
                        CreatorCapabilityEvidence.evidence_type == "commercial_project",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1, [r.capability_key for r in rows]
        assert rows[0].capability_key == "image_generation"


@pytest.mark.asyncio
async def test_rubric_avg_normalized_per_project_max_score(c):
    """R40: rubric_avg must normalize each review by ITS project's max_score.
    A review scored 8 on a max_score=10 project is 80% work — the old code
    averaged raw scores then divided by a fixed 100, pricing it as 0.08."""
    h, owner = await _auth(c)
    oid = await _org(c, h)

    # Project on a 0-10 scale, review scored 8 (= 80%)
    r = await c.post(
        f"/api/v1/orgs/{oid}/projects",
        json={
            "title": "Ten-point project",
            "description": "A commercial project scored on a 10-point scale",
            "instructions": "Deliver the assets described in the brief",
            "max_score": 10,
            "rubric": [{"criterion": "Quality", "max_score": 10}],
        },
        headers=h,
    )
    assert r.status_code == 201, r.text
    project_id = r.json()["data"]["id"]
    await _seed_approved_review(oid, project_id, owner["id"], score=8)

    from types import SimpleNamespace

    from app.core.database import AsyncSessionLocal
    from app.services.matching.scoring import _creator_signals

    async with AsyncSessionLocal() as db:
        spec = SimpleNamespace(org_id=oid, target_entity_type="creator")
        signal_rows = await _creator_signals(
            db, [{"id": owner["id"], "last_login_at": None}], spec, {}
        )
        assert len(signal_rows) == 1
        _, signals = signal_rows[0]
        # 8/10 → 0.8 (old fixed-100 code produced 8/100 = 0.08)
        assert signals["rubric_avg"] == pytest.approx(0.8)


@pytest.mark.asyncio
async def test_assignment_list_scoped_for_students(c):
    """R49: a student sees only THEIR OWN assignments — an unscoped list
    exposed every creator's offer/decline history and the assigner's
    override_reason (recorded discretion) to any org member."""
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_a, creator_a = await _auth(c, "Creator A")
    h_b, creator_b = await _auth(c, "Creator B")
    await _add_member(c, h_owner, oid, creator_a)
    await _add_member(c, h_owner, oid, creator_b)
    project_id = await _project(c, h_owner, oid)

    for uid in (creator_a["id"], creator_b["id"]):
        r = await c.post(
            f"/api/v1/orgs/{oid}/creator-assignments",
            json={
                "project_id": project_id,
                "user_id": uid,
                "override_reason": "private assigner note",
            },
            headers=h_owner,
        )
        assert r.status_code == 201, r.text

    # Owner (instructor+) sees both
    r_owner = await c.get(f"/api/v1/orgs/{oid}/creator-assignments", headers=h_owner)
    assert len(r_owner.json()["data"]) == 2

    # Creator A sees ONLY their own — not B's offer or its override_reason
    r_a = await c.get(f"/api/v1/orgs/{oid}/creator-assignments", headers=h_a)
    rows_a = r_a.json()["data"]
    assert len(rows_a) == 1, rows_a
    assert rows_a[0]["user_id"] == creator_a["id"]

    # Same with the project filter
    r_a2 = await c.get(
        f"/api/v1/orgs/{oid}/creator-assignments?project_id={project_id}", headers=h_a
    )
    assert [x["user_id"] for x in r_a2.json()["data"]] == [creator_a["id"]]


@pytest.mark.asyncio
async def test_creator_match_gated_to_instructors(c):
    """R50: the generic match surface must not be the student side door to
    people-rankings. POST /match with target=creator and reading a persisted
    creator match run are instructor+ (shortlist endpoint's gate)."""
    h_owner, owner = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_student, student = await _auth(c, "Student")
    await _add_member(c, h_owner, oid, student)
    await _completed_skill(c, h_owner, oid, owner["id"], tag="image_generation")
    profile_id = await _confirmed_profile(
        c, h_owner, oid, {"required_capabilities": ["image_generation"]}
    )

    # Student cannot RUN a creator match
    r = await c.post(
        f"/api/v1/orgs/{oid}/match",
        json={"requirement_profile_id": profile_id, "target_entity_type": "creator"},
        headers=h_student,
    )
    assert r.status_code == 403, r.text

    # …but non-people targets stay member-open — for the student's OWN profile.
    # (R89e: a student may not run a match against a peer/instructor's
    # confidential profile; the member-open property is about the target type,
    # not a licence to borrow someone else's profile id.)
    student_profile_id = await _confirmed_profile(
        c, h_student, oid, {"required_capabilities": ["image_generation"]}
    )
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/match",
        json={"requirement_profile_id": student_profile_id, "target_entity_type": "skill_pack"},
        headers=h_student,
    )
    assert r2.status_code == 200, r2.text

    # Owner runs a creator match; the student cannot READ it back
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/match",
        json={"requirement_profile_id": profile_id, "target_entity_type": "creator"},
        headers=h_owner,
    )
    assert r3.status_code == 200, r3.text
    run_id = r3.json()["data"]["id"]

    r4 = await c.get(f"/api/v1/orgs/{oid}/match-runs/{run_id}", headers=h_student)
    assert r4.status_code == 404  # uniform 404 — run ids stay non-enumerable
    r5 = await c.get(f"/api/v1/orgs/{oid}/match-runs/{run_id}", headers=h_owner)
    assert r5.status_code == 200


@pytest.mark.asyncio
async def test_eval_result_evidence_scores_from_total_score(c):
    """R60-#2: eval_result read task.result['overall_score'/'score'] which
    EvaluationService never stores (it stores total_score/max_score) — score
    was ALWAYS None, so every eval_result row scored as a bare 1.0 in
    Bayesian shrinkage, discarding the real grade. Now rescales
    total_score/max_score to 0-100."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    project_id = await _project(c, h, oid)

    from datetime import UTC, datetime

    from app.core.database import AsyncSessionLocal
    from app.models.composer import SolutionDraft
    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask
    from app.models.project import Submission, SubmissionStatus

    async with AsyncSessionLocal() as db:
        db.add(
            SolutionDraft(
                org_id=oid,
                draft_type="production_solution",
                payload={"required_capabilities": [{"capability": "image_generation"}]},
                engine_version="1.0.0",
                status="confirmed",
                materialized_entity_id=project_id,
                created_by=owner["id"],
            )
        )
        sub = Submission(
            org_id=oid,
            project_id=project_id,
            user_id=owner["id"],
            status=SubmissionStatus.APPROVED,
            submitted_at=datetime.now(UTC),
        )
        db.add(sub)
        await db.flush()
        db.add(
            EvaluationTask(
                org_id=oid,
                submission_id=sub.id,
                type=EvalType.SUBMISSION_REVIEW,
                status=EvalStatus.COMPLETED,
                config={},
                # The real shape EvaluationService stores
                result={"total_score": 45, "max_score": 60, "scores": []},
                completed_at=datetime.now(UTC),
            )
        )
        await db.commit()

    from sqlalchemy import select

    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, owner["id"])
        await db.commit()
        rows = list(
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.org_id == oid,
                        CreatorCapabilityEvidence.evidence_type == "eval_result",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1
        # 45/60 * 100 = 75.0 — NOT None
        assert rows[0].score is not None
        assert float(rows[0].score) == pytest.approx(75.0)


@pytest.mark.asyncio
async def test_badge_evidence_requires_full_completion(c):
    """R60-#1: a SkillBadge row exists at ANY progress (completion_pct =
    done/total), so a 20% badge is not mastery. Only a 100% badge is
    capability evidence."""
    h, owner = await _auth(c)
    oid = await _org(c, h)

    cat = (
        await c.post(
            f"/api/v1/orgs/{oid}/categories", json={"name": f"C-{uuid.uuid4().hex[:4]}"}, headers=h
        )
    ).json()["data"]["id"]
    skill_id = (
        await c.post(
            f"/api/v1/orgs/{oid}/skills",
            json={
                "name": f"S-{uuid.uuid4().hex[:4]}",
                "description": "d" * 10,
                "difficulty": "beginner",
                "category_id": cat,
                "tags": ["image_generation"],
            },
            headers=h,
        )
    ).json()["data"]["id"]

    from app.core.database import AsyncSessionLocal
    from app.models.portfolio import SkillBadge

    async with AsyncSessionLocal() as db:
        db.add(
            SkillBadge(
                user_id=owner["id"],
                skill_id=skill_id,
                org_id=oid,
                skill_name="S",
                category_name="C",
                completion_pct=20,
            )
        )
        await db.commit()

    from sqlalchemy import select

    from app.models.composer import CreatorCapabilityEvidence
    from app.services.creator_matching import CreatorMatchingService

    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, owner["id"])
        await db.commit()
        badge_rows = list(
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.org_id == oid,
                        CreatorCapabilityEvidence.evidence_type == "badge",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert badge_rows == []  # 20% badge is not evidence

    # Bump to 100% → now it counts
    async with AsyncSessionLocal() as db:
        b = (
            await db.execute(select(SkillBadge).where(SkillBadge.skill_id == skill_id))
        ).scalar_one()
        b.completion_pct = 100
        await db.commit()
    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, owner["id"])
        await db.commit()
        badge_rows = list(
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.org_id == oid,
                        CreatorCapabilityEvidence.evidence_type == "badge",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert any(r.capability_key == "image_generation" for r in badge_rows)


@pytest.mark.asyncio
async def test_creator_evidence_signal_folds_preferred_caps(c):
    """R60-#3: build_match_requirement demotes extracted required_caps to
    preferred_capabilities (and confirm doesn't re-promote). _creator_signals
    read required_capabilities ONLY → the 0.45-weight capability_evidence
    signal fell into requirement-blind volume mode. It must fold preferred
    caps like the skill_pack path, so a creator with ONLY the requested
    capability's evidence scores on it (not on unrelated volume)."""
    h, owner = await _auth(c)
    oid = await _org(c, h)
    # owner has ONE image_generation evidence row + MANY irrelevant ones.
    # Volume mode (the bug) averages ALL of them → high. Folded mode scores
    # only the requested image_generation cap → the single-row shrinkage.
    await _completed_skill(c, h, oid, owner["id"], tag="image_generation")
    for tag in ("voice_generation", "video_editing", "upscale", "background_removal"):
        await _completed_skill(c, h, oid, owner["id"], tag=tag)

    from types import SimpleNamespace

    from app.core.database import AsyncSessionLocal
    from app.services.creator_matching import CreatorMatchingService
    from app.services.matching.scoring import _creator_signals

    async with AsyncSessionLocal() as db:
        await CreatorMatchingService(db).rebuild_evidence(oid, owner["id"])
        await db.commit()
        spec = SimpleNamespace(org_id=oid, target_entity_type="creator")
        # Capability arrives ONLY under preferred_capabilities (the demoted
        # extraction shape) — required_capabilities empty
        rows = await _creator_signals(
            db,
            [{"id": owner["id"], "last_login_at": None}],
            spec,
            {"preferred_capabilities": ["image_generation"]},
        )
        _, signals = rows[0]
        # Folded mode: only the 1 image_generation row counts → n=1, base 1.0,
        # (1/4)*1.0 + (3/4)*0.5 = 0.625. Volume mode (bug) would average all
        # 5 rows (n=5) → (5/8)*1.0 + (3/8)*0.5 = 0.8125. The gap proves the
        # signal is requirement-scoped, not volume-blind.
        assert signals["capability_evidence"] == pytest.approx(0.625)


@pytest.mark.asyncio
async def test_reoffer_after_decline_supersedes(c):
    """R62: uq_creator_assignment is unconditional on (project, user), so a
    DECLINED offer permanently blocked re-offering. A resolved offer must be
    supersedable — the instructor can revisit a creator who once declined."""
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Creator")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)

    # Offer → creator declines
    r1 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    aid = r1.json()["data"]["id"]
    r2 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": False},
        headers=h_creator,
    )
    assert r2.status_code == 200 and r2.json()["data"]["status"] == "declined"

    # Re-offer must succeed (supersede), not 409
    r3 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={
            "project_id": project_id,
            "user_id": creator["id"],
            "override_reason": "reconsidered",
        },
        headers=h_owner,
    )
    assert r3.status_code == 201, r3.text
    assert r3.json()["data"]["status"] == "offered"

    # But an ACTIVE (offered) one still 409s on double-offer
    r4 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    assert r4.status_code == 409
    assert r4.json()["error"]["code"] == "ASSIGNMENT_EXISTS"

    # The creator can now accept the re-offer
    aid2 = r3.json()["data"]["id"]
    r5 = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid2}/respond",
        json={"accept": True},
        headers=h_creator,
    )
    assert r5.status_code == 200 and r5.json()["data"]["status"] == "accepted"


@pytest.mark.asyncio
async def test_offer_override_reason_nul_rejected(c):
    """R63: override_reason (Text col) accepted NUL -> 500 on write. 422 now."""
    h_owner, _ = await _auth(c, "Owner")
    oid = await _org(c, h_owner)
    h_creator, creator = await _auth(c, "Creator")
    await _add_member(c, h_owner, oid, creator)
    project_id = await _project(c, h_owner, oid)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={
            "project_id": project_id,
            "user_id": creator["id"],
            "override_reason": "a" + chr(0) + "b",
        },
        headers=h_owner,
    )
    assert r.status_code == 422, r.text[:200]


@pytest.mark.asyncio
async def test_withdraw_assignment_lifecycle(c):
    """R64: the assigner can retract a pending offer. Without a withdraw
    path a mis-directed offer was irrevocable (ASSIGNMENT_EXISTS blocks any
    re-offer until the creator happens to decline) even though the state
    machine already supersedes 'withdrawn' rows."""
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
    aid = r.json()["data"]["id"]

    # Withdraw the pending offer
    r = await c.post(f"/api/v1/orgs/{oid}/creator-assignments/{aid}/withdraw", headers=h_owner)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "withdrawn"

    # The creator can no longer accept a withdrawn offer
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": True},
        headers=h_creator,
    )
    assert r.status_code == 409, r.text

    # Re-offer supersedes the withdrawn row IN PLACE (no dup, 201)
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments",
        json={"project_id": project_id, "user_id": creator["id"]},
        headers=h_owner,
    )
    assert r.status_code == 201, r.text
    assert r.json()["data"]["id"] == aid
    assert r.json()["data"]["status"] == "offered"

    # An ACCEPTED offer cannot be withdrawn
    r = await c.post(
        f"/api/v1/orgs/{oid}/creator-assignments/{aid}/respond",
        json={"accept": True},
        headers=h_creator,
    )
    assert r.status_code == 200, r.text
    r = await c.post(f"/api/v1/orgs/{oid}/creator-assignments/{aid}/withdraw", headers=h_owner)
    assert r.status_code == 409, r.text

    # Students cannot withdraw (instructor+ surface)
    r = await c.post(f"/api/v1/orgs/{oid}/creator-assignments/{aid}/withdraw", headers=h_creator)
    assert r.status_code == 403, r.text


# ── R92a: repeated approvals of one submission are single evidence, not N ──


@pytest.mark.asyncio
async def test_approved_submission_evidence_deduped_per_submission(c):
    """R92a: re-review / grade-correction can leave several APPROVED reviews on
    one submission (an allowed instructor action). rebuild_evidence keyed
    approved_submission evidence on review.id, so each re-approval minted
    another weight-1.0 verified-evidence row — an unbounded creator-evidence
    inflation. Evidence must collapse to ONE row per submission (latest approved
    review). Reverting to per-review keying makes this assert >1."""
    import uuid as _uuid
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.models.project import (
        ContentStatus,
        Project,
        ReviewerType,
        ReviewStatus,
        Submission,
        SubmissionReview,
        SubmissionStatus,
    )
    from app.services.creator_matching import CreatorMatchingService

    h, owner = await _auth(c)
    oid = await _org(c, h)

    async with AsyncSessionLocal() as db:
        svc = CreatorMatchingService(db)
        keys = await svc._capability_keys()
        assert keys, "need at least one capability key registered"
        cap = sorted(keys)[0]

        # A project whose project_type IS a capability key → its approved
        # submission attests that capability (branch 1 of _project_capabilities).
        proj = Project(
            org_id=oid,
            title="Dedup Proj",
            slug=f"dedup-{_uuid.uuid4().hex[:8]}",
            description="d",
            instructions="i",
            project_type=cap,
            max_score=100,
            rubric=[{"criterion": "Q", "max_score": 100}],
            status=ContentStatus.PUBLISHED,
            created_by=owner["id"],
        )
        db.add(proj)
        await db.flush()
        sub = Submission(
            org_id=oid,
            project_id=proj.id,
            user_id=owner["id"],
            status=SubmissionStatus.APPROVED,
            version=1,
        )
        db.add(sub)
        await db.flush()
        # Three approved reviews on the SAME submission.
        for i in range(3):
            db.add(
                SubmissionReview(
                    submission_id=sub.id,
                    reviewer_id=owner["id"],
                    reviewer_type=ReviewerType.INSTRUCTOR,
                    status=ReviewStatus.APPROVED,
                    score=80 + i,
                    created_at=datetime(2026, 1, 1 + i, tzinfo=UTC),
                )
            )
        await db.flush()

        await svc.rebuild_evidence(oid, owner["id"])
        await db.commit()

        rows = (
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.user_id == owner["id"],
                        CreatorCapabilityEvidence.evidence_type == "approved_submission",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1, f"expected 1 deduped evidence row, got {len(rows)}"
        # And it carries the LATEST review's score (82 on a max_score-100 scale).
        assert rows[0].evidence_id == sub.id
        assert float(rows[0].score) == 82.0


# ── R92g: a flipped/reopened submission drops its stale APPROVED evidence ──


@pytest.mark.asyncio
async def test_approved_evidence_dropped_when_submission_not_finally_approved(c):
    """R92g: rebuild_evidence filtered on SubmissionReview.status == APPROVED but
    never the submission's FINAL status. A submission approved then reopened
    (revision_requested) or flipped to rejected leaves a stale APPROVED review
    row that kept crediting verified creator evidence for non-approved work.
    Evidence must track the submission's live status. Reverting the
    Submission.status == APPROVED filter makes this credit the rejected work."""
    import uuid as _uuid
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models.composer import CreatorCapabilityEvidence
    from app.models.project import (
        ContentStatus,
        Project,
        ReviewerType,
        ReviewStatus,
        Submission,
        SubmissionReview,
        SubmissionStatus,
    )
    from app.services.creator_matching import CreatorMatchingService

    h, owner = await _auth(c)
    oid = await _org(c, h)

    async with AsyncSessionLocal() as db:
        svc = CreatorMatchingService(db)
        cap = sorted(await svc._capability_keys())[0]
        proj = Project(
            org_id=oid,
            title="Flip Proj",
            slug=f"flip-{_uuid.uuid4().hex[:8]}",
            description="d",
            instructions="i",
            project_type=cap,
            max_score=100,
            rubric=[{"criterion": "Q", "max_score": 100}],
            status=ContentStatus.PUBLISHED,
            created_by=owner["id"],
        )
        db.add(proj)
        await db.flush()
        # Final status REJECTED, but a stale APPROVED review row lingers.
        sub = Submission(
            org_id=oid,
            project_id=proj.id,
            user_id=owner["id"],
            status=SubmissionStatus.REJECTED,
            version=1,
        )
        db.add(sub)
        await db.flush()
        db.add(
            SubmissionReview(
                submission_id=sub.id,
                reviewer_id=owner["id"],
                reviewer_type=ReviewerType.INSTRUCTOR,
                status=ReviewStatus.APPROVED,
                score=90,
                created_at=datetime(2026, 1, 1, tzinfo=UTC),
            )
        )
        await db.flush()

        await svc.rebuild_evidence(oid, owner["id"])
        await db.commit()

        rows = (
            (
                await db.execute(
                    select(CreatorCapabilityEvidence).where(
                        CreatorCapabilityEvidence.user_id == owner["id"],
                        CreatorCapabilityEvidence.evidence_type == "approved_submission",
                    )
                )
            )
            .scalars()
            .all()
        )
        assert rows == [], f"stale approved review credited evidence for rejected work: {rows}"
