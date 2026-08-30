from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.skill import (
    AttemptResponse,
    CategoryResponse,
    CreateCategoryRequest,
    CreateExerciseRequest,
    CreateSkillRequest,
    ExerciseResponse,
    GradeAttemptRequest,
    OverallProgressResponse,
    ReorderRequest,
    SkillDetailResponse,
    SkillProgressResponse,
    SkillProgressSummaryResponse,
    SkillResponse,
    SkillTreeResponse,
    SubmitAttemptRequest,
    UpdateCategoryRequest,
    UpdateExerciseRequest,
    UpdateSkillRequest,
)
from app.services.skill import SkillService

router = APIRouter(tags=["Skills & Exercises"])


class SetPrerequisitesRequest(BaseModel):
    prerequisite_ids: list[str] = []


def _verify_org(resource, org_id: str, label: str = "Resource") -> None:
    """Verify a resource belongs to the specified org (IDOR protection)."""
    if getattr(resource, "org_id", None) != org_id:
        raise HTTPException(status_code=404, detail=f"{label} not found")


_INSTRUCTOR_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
# Grading keys students must never see in exercise config — `correct` is the
# MCQ answer key, `explanation` is the post-answer rationale.
_ANSWER_KEYS = ("correct", "explanation")


def _exercise_response(ex, member) -> ExerciseResponse:
    """Serialize an exercise, stripping answer keys for students."""
    resp = ExerciseResponse.model_validate(ex)
    if member.role not in _INSTRUCTOR_ROLES:
        resp.config = {k: v for k, v in resp.config.items() if k not in _ANSWER_KEYS}
    return resp


def _require_skill_visible(skill, member) -> None:
    """A draft skill's content — including its exercises — is instructor-only
    until published. Mirrors the project/skill read gates (#139/#140)."""
    from app.models.skill import ContentStatus

    if member.role not in _INSTRUCTOR_ROLES and skill.status != ContentStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Skill not found")


# ── Categories ───────────────────────────────────────────


@router.get("/orgs/{org_id}/categories", response_model=DataResponse[list[CategoryResponse]], dependencies=[Depends(rate_limit(20, 60))])
async def list_categories(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    cats = await svc.list_categories(org_id)
    return DataResponse(data=[CategoryResponse.model_validate(c) for c in cats])


@router.post(
    "/orgs/{org_id}/categories", response_model=DataResponse[CategoryResponse], status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_category(
    org_id: str,
    body: CreateCategoryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    cat = await svc.create_category(
        org_id,
        body.name,
        body.slug,
        body.description,
        body.icon,
        user.id,
    )
    await db.commit()
    return DataResponse(data=CategoryResponse.model_validate(cat))


@router.put("/orgs/{org_id}/categories/reorder", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def reorder_categories(
    org_id: str,
    body: ReorderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    for item in body.items:
        cat = await svc.get_category(item.id)
        if cat.org_id != org_id:
            raise HTTPException(status_code=404, detail="Category not in this org")
        await svc.update_category(item.id, sort_order=item.sort_order)
    await db.commit()


@router.put(
    "/orgs/{org_id}/categories/{category_id}", response_model=DataResponse[CategoryResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_category(
    org_id: str,
    category_id: str,
    body: UpdateCategoryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    cat = await svc.get_category(category_id)
    _verify_org(cat, org_id, "Category")
    cat = await svc.update_category(category_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=CategoryResponse.model_validate(cat))


@router.delete("/orgs/{org_id}/categories/{category_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def delete_category(
    org_id: str,
    category_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    cat = await svc.get_category(category_id)
    _verify_org(cat, org_id, "Category")
    await svc.delete_category(category_id)
    await db.commit()


# ── Skills ───────────────────────────────────────────────


@router.get("/orgs/{org_id}/skills", response_model=ListResponse[SkillResponse], dependencies=[Depends(rate_limit(20, 60))])
async def list_skills(
    org_id: str,
    category: str | None = None,
    difficulty: str | None = None,
    status: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    cohort_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = SkillService(db)
    published_only = member.role not in (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    skills, total = await svc.list_skills(
        org_id,
        category,
        difficulty,
        status,
        tag,
        q,
        page,
        per_page,
        published_only=published_only,
        cohort_id=cohort_id,
        user_id=user.id if published_only else None,
    )
    return ListResponse(
        data=[SkillResponse.model_validate(s) for s in skills],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page) < total
        ),
    )


@router.post("/orgs/{org_id}/skills", response_model=DataResponse[SkillResponse], status_code=201, dependencies=[Depends(rate_limit(20, 60))])
async def create_skill(
    org_id: str,
    body: CreateSkillRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.create_skill(
        org_id,
        body.category_id,
        body.name,
        body.slug,
        body.description,
        body.learning_content,
        body.difficulty,
        body.estimated_minutes,
        body.tags,
        body.prerequisites,
        user.id,
    )
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.get("/orgs/{org_id}/skills/{skill_id}", response_model=DataResponse[SkillDetailResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_skill(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    # Draft skills are instructor-only until published (same as projects).
    from app.models.skill import ContentStatus

    if (
        member.role not in (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
        and skill.status != ContentStatus.PUBLISHED
    ):
        raise HTTPException(status_code=404, detail="Skill not found")
    prereqs = await svc.get_skill_prerequisites(skill_id)
    resp = SkillDetailResponse(
        **SkillResponse.model_validate(skill).model_dump(),
        learning_content=skill.learning_content,
        prerequisites=[SkillResponse.model_validate(p) for p in prereqs],
    )
    return DataResponse(data=resp)


@router.put("/orgs/{org_id}/skills/{skill_id}", response_model=DataResponse[SkillResponse], dependencies=[Depends(rate_limit(20, 60))])
async def update_skill(
    org_id: str,
    skill_id: str,
    body: UpdateSkillRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    skill = await svc.update_skill(skill_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.delete("/orgs/{org_id}/skills/{skill_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def delete_skill(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    await svc.delete_skill(skill_id)
    await db.commit()


@router.post("/orgs/{org_id}/skills/{skill_id}/publish", response_model=DataResponse[SkillResponse], dependencies=[Depends(rate_limit(20, 60))])
async def publish_skill(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    skill = await svc.publish_skill(skill_id)
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.post(
    "/orgs/{org_id}/skills/{skill_id}/unpublish", response_model=DataResponse[SkillResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def unpublish_skill(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    skill = await svc.unpublish_skill(skill_id)
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.put("/orgs/{org_id}/skills/{skill_id}/prerequisites", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def set_prerequisites(
    org_id: str,
    skill_id: str,
    body: SetPrerequisitesRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    await svc.set_prerequisites(skill_id, body.prerequisite_ids)
    await db.commit()


# ── Exercises ────────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/skills/{skill_id}/exercises",
    response_model=DataResponse[list[ExerciseResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_exercises(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    _require_skill_visible(skill, member)
    exercises = await svc.list_exercises(skill_id)
    return DataResponse(data=[_exercise_response(e, member) for e in exercises])


@router.get("/orgs/{org_id}/exercises/{exercise_id}", response_model=DataResponse[ExerciseResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_exercise(
    org_id: str,
    exercise_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = SkillService(db)
    ex = await svc.get_exercise(exercise_id)
    if ex.org_id != org_id:
        raise HTTPException(status_code=404, detail="Exercise not found in this organization")
    # An exercise inherits its skill's draft visibility — otherwise a student
    # reads a draft skill's questions via the standalone exercise endpoint.
    skill = await svc.get_skill(ex.skill_id)
    _require_skill_visible(skill, member)
    return DataResponse(data=_exercise_response(ex, member))


@router.post(
    "/orgs/{org_id}/skills/{skill_id}/exercises",
    response_model=DataResponse[ExerciseResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_exercise(
    org_id: str,
    skill_id: str,
    body: CreateExerciseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    ex = await svc.create_exercise(
        org_id,
        skill_id,
        body.title,
        body.description,
        body.type,
        body.config,
        body.max_score,
        user.id,
    )
    await db.commit()
    return DataResponse(data=ExerciseResponse.model_validate(ex))


@router.put("/orgs/{org_id}/exercises/{exercise_id}", response_model=DataResponse[ExerciseResponse], dependencies=[Depends(rate_limit(20, 60))])
async def update_exercise(
    org_id: str,
    exercise_id: str,
    body: UpdateExerciseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    ex = await svc.get_exercise(exercise_id)
    if ex.org_id != org_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Exercise not found in this organization")
    ex = await svc.update_exercise(exercise_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ExerciseResponse.model_validate(ex))


@router.delete("/orgs/{org_id}/exercises/{exercise_id}", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def delete_exercise(
    org_id: str,
    exercise_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    ex = await svc.get_exercise(exercise_id)
    if ex.org_id != org_id:
        raise HTTPException(status_code=404, detail="Exercise not found")
    await svc.delete_exercise(exercise_id)
    await db.commit()


# ── Attempts ─────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/exercises/{exercise_id}/attempts",
    response_model=DataResponse[AttemptResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def submit_attempt(
    org_id: str,
    exercise_id: str,
    body: SubmitAttemptRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    member = await require_org_member(org_id, user, db)
    svc = SkillService(db)
    ex = await svc.get_exercise(exercise_id)
    _verify_org(ex, org_id, "Exercise")
    # Students may only attempt exercises of a PUBLISHED skill; instructors can
    # attempt a draft skill's exercises to test them before publishing.
    from app.models.skill import ContentStatus

    instructor_roles = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    if member.role not in instructor_roles:
        skill = await svc.get_skill(ex.skill_id)
        if skill.status != ContentStatus.PUBLISHED:
            raise HTTPException(status_code=422, detail="Skill is not published")
    attempt = await svc.submit_attempt(org_id, exercise_id, user.id, body.answer)
    await db.commit()
    return DataResponse(data=AttemptResponse.model_validate(attempt))


@router.get(
    "/orgs/{org_id}/exercises/{exercise_id}/attempts",
    response_model=DataResponse[list[AttemptResponse]],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def list_my_attempts(
    org_id: str,
    exercise_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    ex = await svc.get_exercise(exercise_id)
    _verify_org(ex, org_id, "Exercise")
    attempts = await svc.get_user_attempts(exercise_id, user.id)
    return DataResponse(data=[AttemptResponse.model_validate(a) for a in attempts])


# ── Progress ─────────────────────────────────────────────


@router.get("/orgs/{org_id}/progress/me", response_model=DataResponse[OverallProgressResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_my_progress(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    progress = await svc.get_user_progress(user.id, org_id)
    return DataResponse(data=progress)


@router.get(
    "/orgs/{org_id}/progress/me/skills/{skill_id}",
    response_model=DataResponse[SkillProgressResponse | None],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_my_skill_progress(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    progress = await svc.get_skill_progress(skill_id, user.id)
    if progress is None:
        return DataResponse(data=None)
    resp = SkillProgressResponse.model_validate(progress)
    # SkillProgress has no skill_name column — populate it so the field isn't
    # returned as an empty string.
    skill = await svc.get_skill(skill_id)
    resp.skill_name = skill.name
    return DataResponse(data=resp)


# ── Grading ──────────────────────────────────────────────


@router.get("/orgs/{org_id}/grading/pending", response_model=DataResponse[list[AttemptResponse]], dependencies=[Depends(rate_limit(20, 60))])
async def get_pending_grading(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    attempts = await svc.get_pending_grading(org_id)
    return DataResponse(data=[AttemptResponse.model_validate(a) for a in attempts])


@router.post(
    "/orgs/{org_id}/grading/attempts/{attempt_id}", response_model=DataResponse[AttemptResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def grade_attempt(
    org_id: str,
    attempt_id: str,
    body: GradeAttemptRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    attempt = await svc.get_attempt(attempt_id)
    _verify_org(attempt, org_id, "Attempt")
    attempt = await svc.grade_attempt(attempt_id, body.score, body.feedback, grader_id=user.id)
    await db.commit()
    return DataResponse(data=AttemptResponse.model_validate(attempt))


# ── Additional endpoints (audit fixes) ───────────────────


@router.get(
    "/orgs/{org_id}/categories/{category_id}", response_model=DataResponse[CategoryResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def get_category(
    org_id: str,
    category_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    cat = await svc.get_category(category_id)
    _verify_org(cat, org_id, "Category")
    return DataResponse(data=CategoryResponse.model_validate(cat))


@router.put("/orgs/{org_id}/skills/{skill_id}/exercises/reorder", status_code=204, dependencies=[Depends(rate_limit(20, 60))])
async def reorder_exercises(
    org_id: str,
    skill_id: str,
    body: ReorderRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    # Every exercise id must belong to THIS skill — otherwise a caller could
    # reorder (tamper with) another skill's / org's exercises by id.
    for item in body.items:
        ex = await svc.get_exercise(item.id)
        if ex.skill_id != skill_id:
            raise HTTPException(status_code=404, detail="Exercise not in this skill")
        await svc.update_exercise(item.id, sort_order=item.sort_order)
    await db.commit()


@router.get("/orgs/{org_id}/skills/{skill_id}/tree", response_model=DataResponse[SkillTreeResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_skill_tree(
    org_id: str,
    skill_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the skill's prerequisite tree (nodes + edges for visualization)."""
    member = await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    _verify_org(skill, org_id, "Skill")
    from app.models.skill import ContentStatus

    if (
        member.role not in (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
        and skill.status != ContentStatus.PUBLISHED
    ):
        raise HTTPException(status_code=404, detail="Skill not found")
    prereqs = await svc.get_skill_prerequisites(skill_id)
    return DataResponse(
        data=SkillTreeResponse(
            skill=SkillResponse.model_validate(skill),
            prerequisites=[SkillResponse.model_validate(p) for p in prereqs],
        )
    )


@router.get("/orgs/{org_id}/progress/me/skills", response_model=DataResponse[list[SkillProgressSummaryResponse]], dependencies=[Depends(rate_limit(20, 60))])
async def list_my_skill_progress(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get progress for every skill in the org."""
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skills, _total = await svc.list_skills(org_id, per_page=1000)

    # Batch load progress and exercise counts to avoid N+1 queries
    from sqlalchemy import func, select

    from app.models.skill import ContentStatus, Exercise, SkillProgress

    skill_ids = [s.id for s in skills]

    progress_rows = await db.execute(
        select(SkillProgress).where(
            SkillProgress.skill_id.in_(skill_ids),
            SkillProgress.user_id == user.id,
        )
    )
    progress_map = {p.skill_id: p for p in progress_rows.scalars().all()}

    exercise_counts = await db.execute(
        select(Exercise.skill_id, func.count(Exercise.id))
        .where(
            Exercise.skill_id.in_(skill_ids),
            Exercise.status != ContentStatus.ARCHIVED,
        )
        .group_by(Exercise.skill_id)
    )
    exercise_count_map = dict(exercise_counts.all())

    result = []
    for skill in skills:
        progress = progress_map.get(skill.id)
        # The stored snapshot goes stale when exercises are added/archived
        # after the student's last attempt — a skill could show completed 1/1
        # while it actually has 2 exercises. Use the live exercise count and
        # derive the display status from it.
        live_total = exercise_count_map.get(skill.id, 0)
        done = progress.exercises_done if progress else 0
        if done == 0:
            status = "not_started"
        elif live_total > 0 and done >= live_total:
            status = "completed"
        else:
            status = "in_progress"
        result.append(
            SkillProgressSummaryResponse(
                skill_id=skill.id,
                skill_name=skill.name,
                status=status,
                exercises_total=live_total,
                exercises_done=done,
            )
        )
    return DataResponse(data=result)


@router.get("/orgs/{org_id}/progress/students/{student_id}", response_model=DataResponse[OverallProgressResponse], dependencies=[Depends(rate_limit(20, 60))])
async def get_student_progress(
    org_id: str,
    student_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Instructor view: get a specific student's progress."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    progress = await svc.get_user_progress(student_id, org_id)
    return DataResponse(data=progress)
