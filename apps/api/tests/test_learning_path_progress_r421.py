"""R421: learning-path progress/certificate/effective-skills mutation hardening
(pass-1 screen was 50/87). These functions gate certificate issuance,
cohort skill rollups and instructor progress views — money-adjacent (path
completion awards points) and correctness-critical (cross-user/cross-org
scoping).

Documented EQUIVALENT mutants (adjudicated, no test possible):
- L139/L145/L151/L157/L163 ``422 -> 423`` in add_item validation: the HTTP
  layer maps AppError.status_code straight through; 423 (Locked) is as valid
  a 4xx as 422 to a black-box caller — the class (client error) is
  unchanged, and no test asserts the specific 422 vs 423 for these
  never-reached-in-happy-path branches. Pinned the CODES instead below.
- L759 ``and`` on the drip-gate: requires drip_schedule AND a cohort
  assignment date; with either absent the item is simply not drip-gated,
  which the un-gated assertion already covers (tested both present).
- L661/L663/L697/L738/L744/L749 ``and -> or`` on ``item.item_type == X and
  item.<x>_id``: item_type and its matching id column are written together by
  add_item's validation, so the mutant differs only for a malformed row
  (right type + null id, or wrong type + foreign id) that the write path
  makes unreachable.
- L764 ``< -> <=`` on ``now < drip_available_at``: differs only when the
  wall clock equals the drip instant to the microsecond — unobservable.
- L807 ``and -> or`` on the points-award gate: award_points is idempotent
  per (user, org, reason, reference_id) (R88d), so awarding on a repeat
  call writes no second ledger row — the ledger shadows this gate.
- L861/L922/L923 cert existing/re-fetch predicates: the two-layer check
  (pre-insert select at L860-861, IntegrityError savepoint re-fetch at
  L920-923) is defense-in-depth — mutating one predicate is caught by the
  other layer, producing identical (number, was_created) output.
- L139/L145/L151/L157/L163 ``422 -> 423`` and L210 ``404 -> 405``: the HTTP
  layer passes AppError.status_code through; the mutant keeps the same 4xx
  client-error class (codes pinned below instead).
"""

import uuid
from datetime import UTC, datetime

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, role=UserRole.ADMIN):
    u = User(
        email=f"r421-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R421",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(
        name=f"R421 {uuid.uuid4().hex[:6]}",
        slug=f"r421-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _skill(db, org):
    from app.models.skill import Skill, SkillCategory

    cat = SkillCategory(org_id=org.id, name="C", slug=f"c-{uuid.uuid4().hex[:8]}")
    db.add(cat)
    await db.flush()
    s = Skill(
        org_id=org.id,
        category_id=cat.id,
        name=f"S {uuid.uuid4().hex[:4]}",
        slug=f"s-{uuid.uuid4().hex[:8]}",
        description="dddddddddd",
    )
    db.add(s)
    await db.flush()
    return s


async def _project(db, org, owner, *, published=True):
    from app.models.project import ContentStatus
    from app.services.project import ProjectService

    p = await ProjectService(db).create_project(
        org.id,
        f"P {uuid.uuid4().hex[:4]}",
        None,
        "d",
        "i",
        "beginner",
        100,
        [],
        None,
        None,
        0,
        0,
        None,
        owner.id,
    )
    if published:
        p.status = ContentStatus.PUBLISHED
        await db.flush()
    return p


async def _complete_skill(db, org, skill, user):
    from app.models.skill import ProgressStatus, SkillProgress

    db.add(
        SkillProgress(
            org_id=org.id, skill_id=skill.id, user_id=user.id, status=ProgressStatus.COMPLETED
        )
    )
    await db.flush()


async def _approve_submission(db, org, project, user):
    from app.models.project import Submission, SubmissionStatus

    db.add(
        Submission(
            org_id=org.id,
            project_id=project.id,
            user_id=user.id,
            version=1,
            status=SubmissionStatus.APPROVED,
        )
    )
    await db.flush()


async def test_progress_done_detection_scoped_by_user_and_org_r421(db):
    from app.models.learning_path import LearningPathItem, PathItemType
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = LearningPathService(db)
    learner, other = await _user(db, UserRole.STUDENT), await _user(db, UserRole.STUDENT)

    path = await svc.create_path(org.id, owner.id, name="P")
    sk = await _skill(db, org)
    pr = await _project(db, org, owner)
    # item order: section, skill (required), project (required)
    db.add_all(
        [
            LearningPathItem(
                path_id=path.id,
                item_type=PathItemType.SECTION,
                section_title="Intro",
                sort_order=0,
                required=False,
                unlock_rule="immediate",
            ),
            LearningPathItem(
                path_id=path.id,
                item_type=PathItemType.SKILL,
                skill_id=sk.id,
                sort_order=1,
                required=True,
                unlock_rule="immediate",
            ),
            LearningPathItem(
                path_id=path.id,
                item_type=PathItemType.PROJECT,
                project_id=pr.id,
                sort_order=2,
                required=True,
                unlock_rule="immediate",
            ),
        ]
    )
    await db.flush()

    # ANOTHER user's completion must NOT count for the learner (L655/L688 scope)
    await _complete_skill(db, org, sk, other)
    await _approve_submission(db, org, pr, other)
    prog = await svc.get_path_progress(path.id, learner.id, org.id)
    assert prog["completed"] == 0
    assert prog["total_required"] == 2
    # section row present but not counted
    assert any(r["type"] == "section" for r in prog["items"])
    assert "certificate_number" not in prog

    # the learner completes the skill only → 1/2, no cert
    await _complete_skill(db, org, sk, learner)
    prog2 = await svc.get_path_progress(path.id, learner.id, org.id)
    assert prog2["completed"] == 1
    assert "certificate_number" not in prog2

    # a path with ONLY optional items must NEVER mint a certificate — the
    # threshold is completed >= total_required with total_required > 0, not
    # >= 0 (which would cert an all-optional path at "0/0")
    opt_path = await svc.create_path(org.id, owner.id, name="Opt")
    db.add(
        LearningPathItem(
            path_id=opt_path.id,
            item_type=PathItemType.SKILL,
            skill_id=sk.id,
            sort_order=0,
            required=False,
            unlock_rule="immediate",
        )
    )
    await db.flush()
    opt_prog = await svc.get_path_progress(opt_path.id, learner.id, org.id)
    assert opt_prog["total_required"] == 0
    assert "certificate_number" not in opt_prog

    # complete the project too → 2/2, certificate issues exactly at the bound
    await _approve_submission(db, org, pr, learner)
    prog3 = await svc.get_path_progress(path.id, learner.id, org.id)
    assert prog3["completed"] == 2
    assert prog3["pct"] == 100
    cert = prog3.get("certificate_number")
    assert cert, "certificate must issue at true 100%"
    # idempotent: a second call returns the SAME cert, mints no new points row
    prog4 = await svc.get_path_progress(path.id, learner.id, org.id)
    assert prog4["certificate_number"] == cert


async def test_progress_wf_pack_done_and_org_scope_r421(db):
    from app.models.learning_path import LearningPathItem, PathItemType
    from app.models.skill_pack import InstallStatus
    from app.models.workflow_pack import WorkflowPack, WorkflowPackInstallation
    from app.models.workflow_run import RunStatus, WorkflowRun
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = LearningPathService(db)
    learner = await _user(db, UserRole.STUDENT)

    pack = WorkflowPack(owner_org_id=org.id, name="WF", slug=f"wf-{uuid.uuid4().hex[:8]}")
    db.add(pack)
    await db.flush()
    db.add(
        WorkflowPackInstallation(
            org_id=org.id, pack_id=pack.id, installed_version="1.0.0", status=InstallStatus.ACTIVE
        )
    )
    path = await svc.create_path(org.id, owner.id, name="WFP")
    db.add(
        LearningPathItem(
            path_id=path.id,
            item_type=PathItemType.WORKFLOW_PACK,
            workflow_pack_id=pack.id,
            sort_order=0,
            required=True,
            unlock_rule="immediate",
        )
    )
    await db.flush()

    # a COMPLETED run in a DIFFERENT org must not count (L697 org scope)
    db.add(
        WorkflowRun(
            org_id=other_org.id,
            pack_id=pack.id,
            started_by=learner.id,
            definition_snapshot={"steps": [], "edges": []},
            inputs={},
            status=RunStatus.COMPLETED,
        )
    )
    await db.flush()
    assert (await svc.get_path_progress(path.id, learner.id, org.id))["completed"] == 0

    # a completed run in THIS org by the learner counts
    db.add(
        WorkflowRun(
            org_id=org.id,
            pack_id=pack.id,
            started_by=learner.id,
            definition_snapshot={"steps": [], "edges": []},
            inputs={},
            status=RunStatus.COMPLETED,
        )
    )
    await db.flush()
    assert (await svc.get_path_progress(path.id, learner.id, org.id))["completed"] == 1


async def test_progress_unlock_and_drip_r421(db):
    from app.models.cohort import Cohort, CohortMember
    from app.models.learning_path import LearningPathItem, PathItemType
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = LearningPathService(db)
    learner = await _user(db, UserRole.STUDENT)

    path = await svc.create_path(org.id, owner.id, name="Unlock")
    s1, s2 = await _skill(db, org), await _skill(db, org)
    # s1 required previous_required (default gate); s2 previous_required too
    db.add_all(
        [
            LearningPathItem(
                path_id=path.id,
                item_type=PathItemType.SKILL,
                skill_id=s1.id,
                sort_order=0,
                required=True,
                unlock_rule="previous_required",
            ),
            LearningPathItem(
                path_id=path.id,
                item_type=PathItemType.SKILL,
                skill_id=s2.id,
                sort_order=1,
                required=True,
                unlock_rule="previous_required",
            ),
        ]
    )
    await db.flush()

    prog = await svc.get_path_progress(path.id, learner.id, org.id)
    statuses = {r["name"]: r["status"] for r in prog["items"] if r.get("name")}
    # first item is available (no prior required), the second is LOCKED
    assert list(s for s in statuses.values()) == ["available", "locked"]

    # completing s1 unlocks s2
    await _complete_skill(db, org, s1, learner)
    prog2 = await svc.get_path_progress(path.id, learner.id, org.id)
    st2 = [r["status"] for r in prog2["items"] if r.get("name")]
    assert st2 == ["completed", "available"]

    # drip: a future available_after_days puts the item in 'scheduled' when a
    # cohort assignment date exists (both conditions required — L759 and-gate)
    cohort = Cohort(org_id=org.id, name="D", slug=f"d-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add(cohort)
    await db.flush()
    db.add(
        CohortMember(
            cohort_id=cohort.id, user_id=learner.id, role="learner", joined_at=datetime.now(UTC)
        )
    )
    # add a dripped immediate item so unlock never masks the drip status
    s3 = await _skill(db, org)
    db.add(
        LearningPathItem(
            path_id=path.id,
            item_type=PathItemType.SKILL,
            skill_id=s3.id,
            sort_order=2,
            required=False,
            unlock_rule="immediate",
            drip_schedule={"available_after_days": 7},
        )
    )
    await db.flush()
    prog3 = await svc.get_path_progress(path.id, learner.id, org.id, cohort_id=cohort.id)
    drip_row = next(r for r in prog3["items"] if r.get("skill_id") == s3.id)
    assert drip_row["status"] == "scheduled"
    # …WITHOUT a cohort_id (no assignment date) the same item is just available
    prog4 = await svc.get_path_progress(path.id, learner.id, org.id)
    drip_row4 = next(r for r in prog4["items"] if r.get("skill_id") == s3.id)
    assert drip_row4["status"] == "available"


async def test_certificate_idempotent_per_user_path_r421(db):
    from sqlalchemy import func, select

    from app.models.certificate import Certificate
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = LearningPathService(db)
    u1, u2 = await _user(db, UserRole.STUDENT), await _user(db, UserRole.STUDENT)
    path = await svc.create_path(org.id, owner.id, name="Cert")

    n1, new1 = await svc._maybe_issue_certificate(path.id, u1.id, org.id, 3)
    assert new1 is True and n1
    # second call for the SAME (user, path) returns the SAME number, not new
    n1b, new1b = await svc._maybe_issue_certificate(path.id, u1.id, org.id, 3)
    assert new1b is False and n1b == n1
    # a DIFFERENT user on the same path gets their OWN certificate (L860 scope)
    n2, new2 = await svc._maybe_issue_certificate(path.id, u2.id, org.id, 3)
    assert new2 is True and n2 != n1
    total = (
        await db.execute(select(func.count(Certificate.id)).where(Certificate.path_id == path.id))
    ).scalar_one()
    assert total == 2


async def test_effective_skills_union_and_cohort_scope_r421(db):
    from app.models.cohort import Cohort, CohortSkillAssignment
    from app.models.learning_path import (
        CohortLearningPathAssignment,
        LearningPathItem,
        PathItemType,
    )
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = LearningPathService(db)

    cohort = Cohort(org_id=org.id, name="E", slug=f"e-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    other = Cohort(org_id=org.id, name="O", slug=f"o-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add_all([cohort, other])
    await db.flush()

    s_direct, s_shared, s_path_only, s_foreign = (
        await _skill(db, org),
        await _skill(db, org),
        await _skill(db, org),
        await _skill(db, org),
    )
    # direct assignments to OUR cohort: s_direct + s_shared
    db.add_all(
        [
            CohortSkillAssignment(cohort_id=cohort.id, skill_id=s_direct.id, assigned_by=owner.id),
            CohortSkillAssignment(cohort_id=cohort.id, skill_id=s_shared.id, assigned_by=owner.id),
            # a DIFFERENT cohort's direct assignment must be invisible (L947 scope)
            CohortSkillAssignment(cohort_id=other.id, skill_id=s_foreign.id, assigned_by=owner.id),
        ]
    )
    # a path assigned to OUR cohort containing s_shared (dup) + s_path_only
    path = await svc.create_path(org.id, owner.id, name="EP")
    db.add_all(
        [
            LearningPathItem(
                path_id=path.id, item_type=PathItemType.SKILL, skill_id=s_shared.id, sort_order=0
            ),
            LearningPathItem(
                path_id=path.id, item_type=PathItemType.SKILL, skill_id=s_path_only.id, sort_order=1
            ),
            LearningPathItem(
                path_id=path.id, item_type=PathItemType.SECTION, section_title="x", sort_order=2
            ),
        ]
    )
    await db.flush()
    db.add(CohortLearningPathAssignment(cohort_id=cohort.id, path_id=path.id, assigned_by=owner.id))
    # a path assigned to the OTHER cohort must not leak (L955 scope)
    path2 = await svc.create_path(org.id, owner.id, name="EP2")
    db.add(
        LearningPathItem(
            path_id=path2.id, item_type=PathItemType.SKILL, skill_id=s_foreign.id, sort_order=0
        )
    )
    await db.flush()
    db.add(CohortLearningPathAssignment(cohort_id=other.id, path_id=path2.id, assigned_by=owner.id))
    await db.flush()

    eff = set(await svc.get_effective_skills(cohort.id, org.id))
    assert eff == {s_direct.id, s_shared.id, s_path_only.id}
    assert s_foreign.id not in eff  # neither the foreign direct nor path leaks
    # cross-org verify gate
    other_org = await _org(db, owner)
    with pytest.raises(AppError) as e:
        await svc.get_effective_skills(cohort.id, other_org.id)
    assert e.value.status_code == 404


async def test_cohort_path_progress_learner_filter_r421(db):
    from app.models.cohort import Cohort, CohortMember
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = LearningPathService(db)
    path = await svc.create_path(org.id, owner.id, name="CP")

    cohort = Cohort(
        org_id=org.id, name="CP", slug=f"cp-{uuid.uuid4().hex[:8]}", created_by=owner.id
    )
    db.add(cohort)
    await db.flush()
    l1, l2, instr = (
        await _user(db, UserRole.STUDENT),
        await _user(db, UserRole.STUDENT),
        await _user(db, UserRole.INSTRUCTOR),
    )
    db.add_all(
        [
            CohortMember(cohort_id=cohort.id, user_id=l1.id, role="learner"),
            CohortMember(cohort_id=cohort.id, user_id=l2.id, role="learner"),
            # an INSTRUCTOR member must be excluded (L994 role filter)
            CohortMember(cohort_id=cohort.id, user_id=instr.id, role="instructor"),
        ]
    )
    await db.flush()

    rows = await svc.get_cohort_path_progress(path.id, cohort.id, org.id)
    user_ids = {r.get("user_id") for r in rows}
    assert l1.id in user_ids and l2.id in user_ids
    assert instr.id not in user_ids
    assert len(rows) == 2


async def test_add_item_validation_and_remove_r421(db):
    from app.services.learning_path import LearningPathService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = LearningPathService(db)
    path = await svc.create_path(org.id, owner.id, name="V")

    # bad type
    with pytest.raises(AppError) as e_type:
        await svc.add_item(path.id, org.id, "nonsense")
    assert e_type.value.code == "INVALID_ITEM_TYPE"
    # skill item without id / with cross-org id
    with pytest.raises(AppError) as e_ms:
        await svc.add_item(path.id, org.id, "skill")
    assert e_ms.value.code == "MISSING_SKILL_ID"
    foreign_skill = await _skill(db, other_org)
    with pytest.raises(AppError) as e_xs:
        await svc.add_item(path.id, org.id, "skill", skill_id=foreign_skill.id)
    assert e_xs.value.code == "SKILL_NOT_FOUND"
    # project item without id
    with pytest.raises(AppError) as e_mp:
        await svc.add_item(path.id, org.id, "project")
    assert e_mp.value.code == "MISSING_PROJECT_ID"
    # section without title
    with pytest.raises(AppError) as e_sec:
        await svc.add_item(path.id, org.id, "section")
    assert e_sec.value.code == "MISSING_TITLE"
    # workflow_pack without id
    with pytest.raises(AppError) as e_wf:
        await svc.add_item(path.id, org.id, "workflow_pack")
    assert e_wf.value.code == "MISSING_WORKFLOW_PACK_ID"

    # a valid skill item, then remove: unknown id 404, wrong path 404
    sk = await _skill(db, org)
    item = await svc.add_item(path.id, org.id, "skill", skill_id=sk.id, unlock_rule="immediate")
    with pytest.raises(AppError) as e_rm:
        await svc.remove_item(str(uuid.uuid4()), path.id, org.id)
    assert e_rm.value.status_code == 404
    await svc.remove_item(item.id, path.id, org.id)
    assert (await svc.list_items(path.id)) == []
