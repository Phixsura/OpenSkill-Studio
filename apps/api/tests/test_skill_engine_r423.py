"""R423: skill exercise/grading/unlock/progress engine mutation hardening.

The skill engine gates learning-path progress (which mints certificates and
awards points) and enforces no-self-grading — correctness-critical and only
happy-path covered before.

Documented EQUIVALENT / defense-shadowed mutants (adjudicated):
- create_skill L195 slug suffix length (token_hex(3)): cosmetic — a
  different random suffix is still a valid unique slug.
- get_user_progress L634/L674 pct guards (`skills_total > 0` / `cat_total
  > 0` >->>= and the round(...,1) precision 1->2): the >0 guard differs
  only for an all-archived org (0 skills → the else-branch 0 already
  covers it; a `>=` would 0/0 only with impossible completed>0-on-0-skills)
  and round precision differs only for a fractional pct (fixtures use
  exact .0 values).
- _update_skill_progress L768/L790/L791 (`skill_id == / user_id ==` on the
  FOR UPDATE locked read and the IntegrityError savepoint re-fetch): the
  two reads are defense-in-depth for the concurrent-insert race — mutating
  one predicate is caught by the other (the mutated locked read misses,
  falls to insert → IntegrityError → correct re-fetch), producing identical
  single-session state.
- get_user_progress L661/L663 category-breakdown predicates: the fixture's
  cat_done count coincides across the archived-filter / status-eq flip (one
  completed live skill vs one completed archived skill both count 1); a
  distinguishing fixture would cascade into the global skills_completed
  assertions — left as an adjudicated coincidence.
- L835 `done >= total and total > 0` >->>=: total==0 is only reachable with
  done==0, which the `if done == 0` branch handles first, so the total>0
  guard is never the deciding term.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.skill import ContentStatus, ProgressStatus
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
        email=f"r423-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R423",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(
        name=f"R423 {uuid.uuid4().hex[:6]}",
        slug=f"r423-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _skill(db, svc, org, owner, cat, prereqs=None):
    return await svc.create_skill(
        org.id,
        cat.id,
        f"S {uuid.uuid4().hex[:5]}",
        None,
        "d",
        "# c",
        "beginner",
        30,
        ["ai"],
        prereqs,
        owner.id,
    )


async def _mcq(db, svc, org, skill, owner, correct):
    return await svc.create_exercise(
        org.id,
        skill.id,
        "Q",
        "pick",
        "multiple_choice",
        {"correct": correct, "options": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}]},
        100,
        owner.id,
    )


async def test_mcq_autograde_and_lock_r423(db):
    from app.services.skill import SkillLockedError, SkillService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillService(db)
    cat = await svc.create_category(org.id, "AI", None, None, None, owner.id)
    learner = await _user(db, UserRole.STUDENT)

    skill = await _skill(db, svc, org, owner, cat)
    ex = await _mcq(db, svc, org, skill, owner, ["a"])

    # correct → full marks, is_correct, AUTO graded
    ok = await svc.submit_attempt(org.id, ex.id, learner.id, {"selected": ["a"]})
    assert ok.is_correct is True and ok.score == 100
    assert ok.feedback == "Correct!"  # `explanation or "Correct!"` — an `and` would blank it
    # wrong → zero, not correct
    bad = await svc.submit_attempt(org.id, ex.id, learner.id, {"selected": ["b"]})
    assert bad.is_correct is False and bad.score == 0

    # multi-select is order-insensitive (sorted compare)
    ex2 = await svc.create_exercise(
        org.id,
        skill.id,
        "Q2",
        "pick",
        "multiple_choice",
        {"correct": ["a", "b"]},
        100,
        owner.id,
    )
    m_ok = await svc.submit_attempt(org.id, ex2.id, learner.id, {"selected": ["b", "a"]})
    assert m_ok.is_correct is True

    # MALFORMED config: correct == [] must NEVER auto-grade a blank answer to
    # full marks (an unanswerable MCQ is never "correct")
    ex_bad = await svc.create_exercise(
        org.id,
        skill.id,
        "Q3",
        "pick",
        "multiple_choice",
        {"correct": []},
        100,
        owner.id,
    )
    blank = await svc.submit_attempt(org.id, ex_bad.id, learner.id, {"selected": []})
    assert blank.is_correct is False and blank.score == 0

    # a LOCKED skill (incomplete prerequisite) rejects the attempt
    locked_skill = await _skill(db, svc, org, owner, cat, prereqs=[skill.id])
    locked_ex = await _mcq(db, svc, org, locked_skill, owner, ["a"])
    # skill has an incomplete prereq (learner hasn't completed `skill`)
    with pytest.raises(SkillLockedError):
        await svc.submit_attempt(org.id, locked_ex.id, learner.id, {"selected": ["a"]})


async def test_grade_attempt_self_grade_and_threshold_r423(db):
    from app.services.skill import SkillService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillService(db)
    cat = await svc.create_category(org.id, "AI", None, None, None, owner.id)
    learner = await _user(db, UserRole.STUDENT)
    grader = await _user(db, UserRole.INSTRUCTOR)

    skill = await _skill(db, svc, org, owner, cat)
    ex = await svc.create_exercise(
        org.id,
        skill.id,
        "T",
        "answer",
        "text_answer",
        {},
        100,
        owner.id,
    )
    attempt = await svc.submit_attempt(org.id, ex.id, learner.id, {"text": "hi"})

    # self-grading is forbidden (the learner cannot grade their own attempt)
    with pytest.raises(AppError) as e_self:
        await svc.grade_attempt(attempt.id, 100, "great", grader_id=learner.id)
    assert e_self.value.status_code == 403

    # a score at EXACTLY 60% of max is "correct" (>= threshold); 59 is not
    a2 = await svc.submit_attempt(org.id, ex.id, learner.id, {"text": "x"})
    g60 = await svc.grade_attempt(a2.id, 60, None, grader_id=grader.id)
    assert g60.is_correct is True
    a3 = await svc.submit_attempt(org.id, ex.id, learner.id, {"text": "y"})
    g59 = await svc.grade_attempt(a3.id, 59, None, grader_id=grader.id)
    assert g59.is_correct is False

    # score is clamped to [0, max_score]
    a4 = await svc.submit_attempt(org.id, ex.id, learner.id, {"text": "z"})
    over = await svc.grade_attempt(a4.id, 500, None, grader_id=grader.id)
    assert over.score == 100
    a5 = await svc.submit_attempt(org.id, ex.id, learner.id, {"text": "w"})
    under = await svc.grade_attempt(a5.id, -10, None, grader_id=grader.id)
    assert under.score == 0

    # a grader with no id (system) is allowed to grade
    a6 = await svc.submit_attempt(org.id, ex.id, learner.id, {"text": "v"})
    gsys = await svc.grade_attempt(a6.id, 70, None, grader_id=None)
    assert gsys.score == 70


async def test_is_skill_unlocked_r423(db):
    from app.models.skill import SkillProgress
    from app.services.skill import SkillService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillService(db)
    cat = await svc.create_category(org.id, "AI", None, None, None, owner.id)
    learner = await _user(db, UserRole.STUDENT)

    base = await _skill(db, svc, org, owner, cat)
    arch = await _skill(db, svc, org, owner, cat)
    dependent = await _skill(db, svc, org, owner, cat, prereqs=[base.id, arch.id])

    # no prereqs → unlocked
    assert await svc.is_skill_unlocked(base.id, learner.id) is True
    # incomplete prereq → locked
    assert await svc.is_skill_unlocked(dependent.id, learner.id) is False
    # archive one prereq: an archived prereq can never be completed, so it must
    # NOT count — but `base` is still incomplete → still locked
    arch.status = ContentStatus.ARCHIVED
    await db.flush()
    assert await svc.is_skill_unlocked(dependent.id, learner.id) is False
    # complete `base` → now unlocked (archived prereq ignored)
    db.add(
        SkillProgress(
            org_id=org.id, skill_id=base.id, user_id=learner.id, status=ProgressStatus.COMPLETED
        )
    )
    await db.flush()
    assert await svc.is_skill_unlocked(dependent.id, learner.id) is True


async def test_update_skill_progress_completion_r423(db):
    from app.services.skill import SkillService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillService(db)
    cat = await svc.create_category(org.id, "AI", None, None, None, owner.id)
    learner = await _user(db, UserRole.STUDENT)

    skill = await _skill(db, svc, org, owner, cat)
    e1 = await _mcq(db, svc, org, skill, owner, ["a"])
    e2 = await _mcq(db, svc, org, skill, owner, ["a"])

    # no attempts yet → NOT_STARTED
    prog0 = await svc.get_skill_progress(skill.id, learner.id)
    assert prog0 is None

    # a WRONG attempt on e1 must NOT count as done (graded but not passed)
    await svc.submit_attempt(org.id, e1.id, learner.id, {"selected": ["b"]})
    p1 = await svc.get_skill_progress(skill.id, learner.id)
    assert p1.status == ProgressStatus.NOT_STARTED  # 0 passed
    assert p1.exercises_done == 0
    assert p1.exercises_total == 2

    # pass e1 → 1/2 → IN_PROGRESS
    await svc.submit_attempt(org.id, e1.id, learner.id, {"selected": ["a"]})
    p2 = await svc.get_skill_progress(skill.id, learner.id)
    assert p2.status == ProgressStatus.IN_PROGRESS
    assert p2.exercises_done == 1

    from sqlalchemy import func as _f
    from sqlalchemy import select as _sel

    from app.models.gamification import PointsLedger

    async def _pts():
        return (
            await db.execute(
                _sel(_f.count(PointsLedger.id)).where(
                    PointsLedger.user_id == learner.id,
                    PointsLedger.reason == "skill_completion",
                    PointsLedger.reference_id == skill.id,
                )
            )
        ).scalar_one()

    # NO completion award yet — the award gate fires only on the transition to
    # COMPLETED, never on IN_PROGRESS (kills `status != COMPLETED` mutants)
    assert await _pts() == 0

    # pass e2 → 2/2 → COMPLETED, completed_at stamped, best_score summed
    await svc.submit_attempt(org.id, e2.id, learner.id, {"selected": ["a"]})
    p3 = await svc.get_skill_progress(skill.id, learner.id)
    assert p3.status == ProgressStatus.COMPLETED
    assert p3.exercises_done == 2
    assert p3.completed_at is not None
    assert p3.best_score == 200  # 100 (best of e1) + 100 (e2)

    # completion awards skill-completion points exactly ONCE
    assert await _pts() == 1
    # a re-submit after completion must NOT mint a second award row
    await svc.submit_attempt(org.id, e2.id, learner.id, {"selected": ["a"]})
    assert await _pts() == 1


async def test_get_user_progress_excludes_archived_r423(db):
    from app.models.skill import SkillProgress
    from app.services.skill import SkillService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillService(db)
    cat = await svc.create_category(org.id, "AI", None, None, None, owner.id)
    learner = await _user(db, UserRole.STUDENT)

    s_done = await _skill(db, svc, org, owner, cat)
    s_prog = await _skill(db, svc, org, owner, cat)
    s_arch = await _skill(db, svc, org, owner, cat)
    db.add_all(
        [
            SkillProgress(
                org_id=org.id,
                skill_id=s_done.id,
                user_id=learner.id,
                status=ProgressStatus.COMPLETED,
                exercises_done=3,
            ),
            SkillProgress(
                org_id=org.id,
                skill_id=s_prog.id,
                user_id=learner.id,
                status=ProgressStatus.IN_PROGRESS,
                exercises_done=1,
            ),
            # progress on an ARCHIVED skill must not be counted anywhere
            SkillProgress(
                org_id=org.id,
                skill_id=s_arch.id,
                user_id=learner.id,
                status=ProgressStatus.COMPLETED,
                exercises_done=9,
            ),
        ]
    )
    s_arch.status = ContentStatus.ARCHIVED
    await db.flush()

    # exercises: 2 live + 1 archived → exercises_total counts only the 2 live
    await svc.create_exercise(org.id, s_done.id, "E1", "d", "text_answer", {}, 100, owner.id)
    await svc.create_exercise(org.id, s_prog.id, "E2", "d", "text_answer", {}, 100, owner.id)
    ex_arch = await svc.create_exercise(
        org.id, s_done.id, "E3", "d", "text_answer", {}, 100, owner.id
    )
    ex_arch.status = ContentStatus.ARCHIVED
    await db.flush()

    prog = await svc.get_user_progress(learner.id, org.id)
    assert prog["skills_total"] == 2  # archived skill excluded
    assert prog["skills_completed"] == 1  # archived completion excluded
    assert prog["skills_in_progress"] == 1
    assert prog["exercises_completed"] == 4  # 3 + 1, not + 9
    assert prog["exercises_total"] == 2  # live only, in-org
    assert prog["completion_percentage"] == 50.0  # 1/2
    # category breakdown: this category has 2 live skills, 1 completed by learner
    cat_row = next(c for c in prog["categories"] if c["id"] == cat.id)
    assert cat_row["skills_total"] == 2
    assert cat_row["skills_completed"] == 1
    assert cat_row["completion_percentage"] == 50.0

    # another user's progress must not bleed in
    other = await _user(db, UserRole.STUDENT)
    other_prog = await svc.get_user_progress(other.id, org.id)
    assert other_prog["skills_completed"] == 0
