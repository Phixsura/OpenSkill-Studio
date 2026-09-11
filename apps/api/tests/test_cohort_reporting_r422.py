"""R422: cohort service guards + progress/reporting math mutation hardening.

The cohort dashboard aggregates (get_cohort_progress / drill-down) drive
instructor decisions and the guards gate who joins a paid cohort — both
were only lightly covered by the HTTP/adversarial suites.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.cohort import CohortRole, CohortStatus
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
        email=f"r422-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R422",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(
        name=f"R422 {uuid.uuid4().hex[:6]}",
        slug=f"r422-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _member(db, org, svc_org, role=UserRole.STUDENT):
    from app.models.organization import OrgRole

    u = await _user(db, role)
    await svc_org.add_member(org.id, u.id, OrgRole.STUDENT)
    return u


async def _skill(db, org):
    from app.models.skill import Skill, SkillCategory

    cat = SkillCategory(org_id=org.id, name="C", slug=f"c-{uuid.uuid4().hex[:8]}")
    db.add(cat)
    await db.flush()
    s = Skill(org_id=org.id, category_id=cat.id, name=f"S {uuid.uuid4().hex[:4]}",
              slug=f"s-{uuid.uuid4().hex[:8]}", description="dddddddddd")
    db.add(s)
    await db.flush()
    return s


async def _project(db, org, owner, *, published=True, deadline=None):
    from app.models.project import ContentStatus
    from app.services.project import ProjectService

    p = await ProjectService(db).create_project(
        org.id, f"P {uuid.uuid4().hex[:4]}", None, "d", "i", "beginner", 100,
        [], deadline, None, 0, 0, None, owner.id,
    )
    if published:
        p.status = ContentStatus.PUBLISHED
        await db.flush()
    return p


async def test_add_member_guards_r422(db):
    from app.services.cohort import (
        AlreadyCohortMemberError,
        CohortFullError,
        CohortNotFoundError,
        CohortService,
    )
    from app.services.organization import OrgService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    org_svc = OrgService(db)
    svc = CohortService(db)
    cohort = await svc.create_cohort(org.id, "C", None, max_learners=2, created_by=owner.id)

    # a NON-org-member user → USER_NOT_FOUND 404 (never an FK 500)
    stranger = await _user(db, UserRole.STUDENT)
    with pytest.raises(AppError) as e_nm:
        await svc.add_member(cohort.id, stranger.id, CohortRole.LEARNER, org.id)
    assert e_nm.value.status_code == 404

    # wrong org → cohort not found (no cross-org add)
    l1 = await _member(db, org, org_svc)
    with pytest.raises(CohortNotFoundError):
        await svc.add_member(cohort.id, l1.id, CohortRole.LEARNER, other_org.id)

    # add one learner, then a duplicate add → AlreadyCohortMember (cohort not
    # yet full, so the dedup insert — not the cap — is what fires)
    await svc.add_member(cohort.id, l1.id, CohortRole.LEARNER, org.id)
    with pytest.raises(AlreadyCohortMemberError):
        await svc.add_member(cohort.id, l1.id, CohortRole.LEARNER, org.id)

    # fill the learner cap of 2; the 3rd LEARNER is rejected AT the bound
    l2, l3 = await _member(db, org, org_svc), await _member(db, org, org_svc)
    await svc.add_member(cohort.id, l2.id, CohortRole.LEARNER, org.id)
    with pytest.raises(CohortFullError):
        await svc.add_member(cohort.id, l3.id, CohortRole.LEARNER, org.id)
    # …but an INSTRUCTOR does NOT count against the learner cap
    instr = await _member(db, org, org_svc)
    m_instr = await svc.add_member(cohort.id, instr.id, CohortRole.INSTRUCTOR, org.id)
    assert m_instr.role == CohortRole.INSTRUCTOR

    # a COMPLETED cohort is frozen for adds; ARCHIVED reads as not-found
    cohort.status = CohortStatus.COMPLETED
    await db.flush()
    l4 = await _member(db, org, org_svc)
    with pytest.raises(AppError) as e_frozen:
        await svc.add_member(cohort.id, l4.id, CohortRole.LEARNER, org.id)
    assert e_frozen.value.code == "COHORT_FROZEN"
    cohort.status = CohortStatus.ARCHIVED
    await db.flush()
    with pytest.raises(CohortNotFoundError):
        await svc.add_member(cohort.id, l4.id, CohortRole.LEARNER, org.id)


async def test_assign_skill_and_project_guards_r422(db):
    from app.models.project import ContentStatus
    from app.services.cohort import CohortNotFoundError, CohortService
    from app.services.organization import OrgService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    OrgService(db)
    svc = CohortService(db)
    cohort = await svc.create_cohort(org.id, "C", None, created_by=owner.id)

    # cross-org skill / archived skill → 404
    foreign_skill = await _skill(db, other_org)
    with pytest.raises(AppError) as e_xs:
        await svc.assign_skill(cohort.id, foreign_skill.id, org.id, owner.id)
    assert e_xs.value.code == "SKILL_NOT_FOUND"
    sk = await _skill(db, org)
    sk.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(AppError) as e_arch:
        await svc.assign_skill(cohort.id, sk.id, org.id, owner.id)
    assert e_arch.value.code == "SKILL_NOT_FOUND"

    # valid assign, then duplicate → 409
    sk2 = await _skill(db, org)
    await svc.assign_skill(cohort.id, sk2.id, org.id, owner.id)
    with pytest.raises(AppError) as e_dup:
        await svc.assign_skill(cohort.id, sk2.id, org.id, owner.id)
    assert e_dup.value.status_code == 409

    # project: unpublished → 422, cross-org → 404, published dup → 409
    draft_proj = await _project(db, org, owner, published=False)
    with pytest.raises(AppError) as e_unpub:
        await svc.assign_project(cohort.id, draft_proj.id, org.id, owner.id)
    assert e_unpub.value.code == "PROJECT_NOT_PUBLISHED"
    foreign_proj = await _project(db, other_org, owner)
    with pytest.raises(AppError) as e_xp:
        await svc.assign_project(cohort.id, foreign_proj.id, org.id, owner.id)
    assert e_xp.value.code == "PROJECT_NOT_FOUND"
    proj = await _project(db, org, owner)
    a = await svc.assign_project(cohort.id, proj.id, org.id, owner.id,
                                 participation_mode="not_a_mode")
    from app.models.cohort import ParticipationMode
    assert a.participation_mode == ParticipationMode.ASSIGNED  # bad mode → fallback
    with pytest.raises(AppError) as e_pdup:
        await svc.assign_project(cohort.id, proj.id, org.id, owner.id)
    assert e_pdup.value.status_code == 409

    # frozen cohort rejects both assigns
    cohort.status = CohortStatus.COMPLETED
    await db.flush()
    sk3 = await _skill(db, org)
    with pytest.raises(AppError) as e_fs:
        await svc.assign_skill(cohort.id, sk3.id, org.id, owner.id)
    assert e_fs.value.code == "COHORT_FROZEN"

    # cross-org get_cohort_progress → not found
    with pytest.raises(CohortNotFoundError):
        await svc.get_cohort_progress(cohort.id, other_org.id)


async def test_cohort_progress_math_r422(db):
    from app.models.project import Submission, SubmissionStatus
    from app.models.skill import ProgressStatus, SkillProgress
    from app.services.cohort import CohortService
    from app.services.organization import OrgService

    owner = await _user(db)
    org = await _org(db, owner)
    org_svc = OrgService(db)
    svc = CohortService(db)
    cohort = await svc.create_cohort(org.id, "Prog", None, created_by=owner.id)

    # 2 learners + 1 instructor (instructor must NOT enter learner counts)
    la, lb = await _member(db, org, org_svc), await _member(db, org, org_svc)
    instr = await _member(db, org, org_svc)
    await svc.add_member(cohort.id, la.id, CohortRole.LEARNER, org.id)
    await svc.add_member(cohort.id, lb.id, CohortRole.LEARNER, org.id)
    await svc.add_member(cohort.id, instr.id, CohortRole.INSTRUCTOR, org.id)

    # 2 skills; la completes ONE → avg_skill_completion = 1/(2*2) = 25.0%
    s1, s2 = await _skill(db, org), await _skill(db, org)
    await svc.assign_skill(cohort.id, s1.id, org.id, owner.id)
    await svc.assign_skill(cohort.id, s2.id, org.id, owner.id)
    db.add(SkillProgress(org_id=org.id, skill_id=s1.id, user_id=la.id,
                         status=ProgressStatus.COMPLETED))
    # the instructor completing a skill must NOT move the learner average
    db.add(SkillProgress(org_id=org.id, skill_id=s2.id, user_id=instr.id,
                         status=ProgressStatus.COMPLETED))
    await db.flush()

    # an OVERDUE project (deadline in the past)
    proj = await _project(db, org, owner, deadline=datetime.now(UTC) - timedelta(days=1))
    await svc.assign_project(cohort.id, proj.id, org.id, owner.id)
    # la submitted (best=submitted); lb has only a draft → counts as overdue
    db.add(Submission(org_id=org.id, project_id=proj.id, user_id=la.id, version=1,
                      status=SubmissionStatus.SUBMITTED))
    db.add(Submission(org_id=org.id, project_id=proj.id, user_id=lb.id, version=1,
                      status=SubmissionStatus.DRAFT))
    await db.flush()

    prog = await svc.get_cohort_progress(cohort.id, org.id)
    assert prog["total_learners"] == 2  # instructor excluded
    assert prog["total_skills_assigned"] == 2
    assert prog["avg_skill_completion_pct"] == 25.0
    pj = prog["projects"][0]
    assert pj["submitted"] == 1
    assert pj["not_started"] == 0  # both learners have a submission row
    # overdue = not_started + draft + revision = 0 + 1 + 0 = 1 (lb's draft)
    assert pj["overdue"] == 1
    assert prog["overdue_submissions"] == 1
    assert pj["total_assignees"] == 2


async def test_learner_drill_down_r422(db):
    from app.models.project import Submission, SubmissionStatus
    from app.services.cohort import CohortService
    from app.services.organization import OrgService

    owner = await _user(db)
    org = await _org(db, owner)
    org_svc = OrgService(db)
    svc = CohortService(db)
    cohort = await svc.create_cohort(org.id, "Drill", None, created_by=owner.id)
    la = await _member(db, org, org_svc)
    outsider = await _member(db, org, org_svc)
    await svc.add_member(cohort.id, la.id, CohortRole.LEARNER, org.id)

    # a non-member → NOT_COHORT_MEMBER 404
    with pytest.raises(AppError) as e_nm:
        await svc.get_learner_drill_down(cohort.id, outsider.id, org.id)
    assert e_nm.value.status_code == 404

    proj = await _project(db, org, owner, deadline=datetime.now(UTC) - timedelta(days=1))
    await svc.assign_project(cohort.id, proj.id, org.id, owner.id)
    # a DRAFT past the deadline is overdue; the newest version is reported
    db.add(Submission(org_id=org.id, project_id=proj.id, user_id=la.id, version=1,
                      status=SubmissionStatus.SUBMITTED))
    db.add(Submission(org_id=org.id, project_id=proj.id, user_id=la.id, version=2,
                      status=SubmissionStatus.DRAFT))
    await db.flush()

    dd = await svc.get_learner_drill_down(cohort.id, la.id, org.id)
    proj_row = dd["projects"][0]
    assert proj_row["submission_status"] == "draft"  # newest version wins
    assert proj_row["is_overdue"] is True
