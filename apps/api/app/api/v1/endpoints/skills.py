from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
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
    SkillResponse,
    SubmitAttemptRequest,
    UpdateCategoryRequest,
    UpdateExerciseRequest,
    UpdateSkillRequest,
)
from app.services.skill import SkillService

router = APIRouter(tags=["Skills & Exercises"])




# ── Categories ───────────────────────────────────────────


@router.get("/orgs/{org_id}/categories", response_model=DataResponse[list[CategoryResponse]])
async def list_categories(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    cats = await svc.list_categories(org_id)
    return DataResponse(data=[CategoryResponse.model_validate(c) for c in cats])


@router.post("/orgs/{org_id}/categories", response_model=DataResponse[CategoryResponse], status_code=201)
async def create_category(
    org_id: str,
    body: CreateCategoryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    cat = await svc.create_category(
        org_id, body.name, body.slug, body.description, body.icon, user.id,
    )
    await db.commit()
    return DataResponse(data=CategoryResponse.model_validate(cat))


@router.put("/orgs/{org_id}/categories/reorder", status_code=200)
async def reorder_categories(
    org_id: str, body: ReorderRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    for item in body.items:
        await svc.update_category(item.id, sort_order=item.sort_order)
    await db.commit()
    return {"message": "Categories reordered"}


@router.put("/orgs/{org_id}/categories/{category_id}", response_model=DataResponse[CategoryResponse])
async def update_category(
    org_id: str, category_id: str, body: UpdateCategoryRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    cat = await svc.update_category(category_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=CategoryResponse.model_validate(cat))


@router.delete("/orgs/{org_id}/categories/{category_id}", status_code=204)
async def delete_category(
    org_id: str, category_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    await svc.delete_category(category_id)
    await db.commit()


# ── Skills ───────────────────────────────────────────────


@router.get("/orgs/{org_id}/skills", response_model=ListResponse[SkillResponse])
async def list_skills(
    org_id: str, category: str | None = None, difficulty: str | None = None,
    status: str | None = None, tag: str | None = None, q: str | None = None,
    page: int = 1, per_page: int = 20,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skills, total = await svc.list_skills(org_id, category, difficulty, status, tag, q, page, per_page)
    return ListResponse(
        data=[SkillResponse.model_validate(s) for s in skills],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.post("/orgs/{org_id}/skills", response_model=DataResponse[SkillResponse], status_code=201)
async def create_skill(
    org_id: str, body: CreateSkillRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.create_skill(
        org_id, body.category_id, body.name, body.slug, body.description,
        body.learning_content, body.difficulty, body.estimated_minutes,
        body.tags, body.prerequisites, user.id,
    )
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.get("/orgs/{org_id}/skills/{skill_id}", response_model=DataResponse[SkillDetailResponse])
async def get_skill(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    prereqs = await svc.get_skill_prerequisites(skill_id)
    resp = SkillDetailResponse(
        **SkillResponse.model_validate(skill).model_dump(),
        learning_content=skill.learning_content,
        prerequisites=[SkillResponse.model_validate(p) for p in prereqs],
    )
    return DataResponse(data=resp)


@router.put("/orgs/{org_id}/skills/{skill_id}", response_model=DataResponse[SkillResponse])
async def update_skill(
    org_id: str, skill_id: str, body: UpdateSkillRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.update_skill(skill_id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.delete("/orgs/{org_id}/skills/{skill_id}", status_code=204)
async def delete_skill(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    await svc.delete_skill(skill_id)
    await db.commit()


@router.post("/orgs/{org_id}/skills/{skill_id}/publish", response_model=DataResponse[SkillResponse])
async def publish_skill(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.publish_skill(skill_id)
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.post("/orgs/{org_id}/skills/{skill_id}/unpublish", response_model=DataResponse[SkillResponse])
async def unpublish_skill(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    skill = await svc.unpublish_skill(skill_id)
    await db.commit()
    return DataResponse(data=SkillResponse.model_validate(skill))


@router.put("/orgs/{org_id}/skills/{skill_id}/prerequisites", status_code=200)
async def set_prerequisites(
    org_id: str, skill_id: str, body: dict,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    prerequisite_ids = body.get("prerequisite_ids", [])
    svc = SkillService(db)
    await svc.set_prerequisites(skill_id, prerequisite_ids)
    await db.commit()
    return {"message": "Prerequisites updated"}


# ── Exercises ────────────────────────────────────────────


@router.get("/orgs/{org_id}/skills/{skill_id}/exercises", response_model=DataResponse[list[ExerciseResponse]])
async def list_exercises(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    exercises = await svc.list_exercises(skill_id)
    return DataResponse(data=[ExerciseResponse.model_validate(e) for e in exercises])


@router.get("/orgs/{org_id}/exercises/{exercise_id}", response_model=DataResponse[ExerciseResponse])
async def get_exercise(
    org_id: str, exercise_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    ex = await svc.get_exercise(exercise_id)
    if ex.org_id != org_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Exercise not found in this organization")
    return DataResponse(data=ExerciseResponse.model_validate(ex))


@router.post(
    "/orgs/{org_id}/skills/{skill_id}/exercises",
    response_model=DataResponse[ExerciseResponse], status_code=201,
)
async def create_exercise(
    org_id: str, skill_id: str, body: CreateExerciseRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    ex = await svc.create_exercise(
        org_id, skill_id, body.title, body.description, body.type, body.config, body.max_score, user.id,
    )
    await db.commit()
    return DataResponse(data=ExerciseResponse.model_validate(ex))


@router.put("/orgs/{org_id}/exercises/{exercise_id}", response_model=DataResponse[ExerciseResponse])
async def update_exercise(
    org_id: str, exercise_id: str, body: UpdateExerciseRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
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


@router.delete("/orgs/{org_id}/exercises/{exercise_id}", status_code=204)
async def delete_exercise(
    org_id: str, exercise_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    await svc.delete_exercise(exercise_id)
    await db.commit()


# ── Attempts ─────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/exercises/{exercise_id}/attempts",
    response_model=DataResponse[AttemptResponse], status_code=201,
)
async def submit_attempt(
    org_id: str, exercise_id: str, body: SubmitAttemptRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    attempt = await svc.submit_attempt(org_id, exercise_id, user.id, body.answer)
    await db.commit()
    return DataResponse(data=AttemptResponse.model_validate(attempt))


@router.get(
    "/orgs/{org_id}/exercises/{exercise_id}/attempts",
    response_model=DataResponse[list[AttemptResponse]],
)
async def list_my_attempts(
    org_id: str, exercise_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    attempts = await svc.get_user_attempts(exercise_id, user.id)
    return DataResponse(data=[AttemptResponse.model_validate(a) for a in attempts])


# ── Progress ─────────────────────────────────────────────


@router.get("/orgs/{org_id}/progress/me", response_model=OverallProgressResponse)
async def get_my_progress(
    org_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    return await svc.get_user_progress(user.id, org_id)


@router.get("/orgs/{org_id}/progress/me/skills/{skill_id}", response_model=DataResponse[SkillProgressResponse | None])
async def get_my_skill_progress(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    progress = await svc.get_skill_progress(skill_id, user.id)
    if progress is None:
        return DataResponse(data=None)
    resp = SkillProgressResponse.model_validate(progress)
    return DataResponse(data=resp)


# ── Grading ──────────────────────────────────────────────


@router.get("/orgs/{org_id}/grading/pending", response_model=DataResponse[list[AttemptResponse]])
async def get_pending_grading(
    org_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    attempts = await svc.get_pending_grading(org_id)
    return DataResponse(data=[AttemptResponse.model_validate(a) for a in attempts])


@router.post("/orgs/{org_id}/grading/attempts/{attempt_id}", response_model=DataResponse[AttemptResponse])
async def grade_attempt(
    org_id: str, attempt_id: str, body: GradeAttemptRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    attempt = await svc.grade_attempt(attempt_id, body.score, body.feedback)
    await db.commit()
    return DataResponse(data=AttemptResponse.model_validate(attempt))


# ── Additional endpoints (audit fixes) ───────────────────


@router.get("/orgs/{org_id}/categories/{category_id}", response_model=DataResponse[CategoryResponse])
async def get_category(
    org_id: str, category_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    cat = await svc.get_category(category_id)
    return DataResponse(data=CategoryResponse.model_validate(cat))



@router.put("/orgs/{org_id}/skills/{skill_id}/exercises/reorder", status_code=200)
async def reorder_exercises(
    org_id: str, skill_id: str, body: ReorderRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    for item in body.items:
        await svc.update_exercise(item.id, sort_order=item.sort_order)
    await db.commit()
    return {"message": "Exercises reordered"}


@router.get("/orgs/{org_id}/skills/{skill_id}/tree")
async def get_skill_tree(
    org_id: str, skill_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    """Get the skill's prerequisite tree (nodes + edges for visualization)."""
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skill = await svc.get_skill(skill_id)
    prereqs = await svc.get_skill_prerequisites(skill_id)
    return {
        "skill": SkillResponse.model_validate(skill),
        "prerequisites": [SkillResponse.model_validate(p) for p in prereqs],
    }


@router.get("/orgs/{org_id}/progress/me/skills")
async def list_my_skill_progress(
    org_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    """Get progress for every skill in the org."""
    await require_org_member(org_id, user, db)
    svc = SkillService(db)
    skills, _total = await svc.list_skills(org_id, per_page=1000)
    result = []
    for skill in skills:
        progress = await svc.get_skill_progress(skill.id, user.id)
        result.append({
            "skill_id": skill.id,
            "skill_name": skill.name,
            "status": progress.status.value if progress else "not_started",
            "exercises_total": progress.exercises_total if progress else 0,
            "exercises_done": progress.exercises_done if progress else 0,
        })
    return DataResponse(data=result)


@router.get("/orgs/{org_id}/progress/students/{student_id}")
async def get_student_progress(
    org_id: str, student_id: str,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    """Instructor view: get a specific student's progress."""
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
    svc = SkillService(db)
    return await svc.get_user_progress(student_id, org_id)
