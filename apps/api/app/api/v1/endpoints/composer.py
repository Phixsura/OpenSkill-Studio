"""Composer + creator-assignment endpoints (ADR-013).

Drafts are the single side-effect gate: composing writes only draft rows;
POST /confirm (a human action) materializes real entities. Assignments are
offers — the platform never auto-assigns.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.composer import (
    AssignmentResponse,
    ComposeRequest,
    ConfirmResponse,
    DraftResponse,
    OfferAssignmentRequest,
    RespondRequest,
    ShortlistCreator,
    ShortlistResponse,
    UpdateDraftRequest,
)
from app.services.creator_matching import CreatorMatchingService
from app.services.learning_composer import LearningComposerService
from app.services.production_composer import ProductionComposerService

router = APIRouter(tags=["Composer"])

WRITE_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)


# ── Compose drafts ────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/drafts/learning-path",
    response_model=DataResponse[DraftResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def compose_learning_path(
    org_id: str,
    body: ComposeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = LearningComposerService(db)
    draft = await svc.compose(org_id, body.profile_id, created_by=user.id)
    await db.commit()
    return DataResponse(data=DraftResponse.model_validate(draft))


@router.post(
    "/orgs/{org_id}/drafts/production-solution",
    response_model=DataResponse[DraftResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def compose_production_solution(
    org_id: str,
    body: ComposeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = ProductionComposerService(db)
    draft = await svc.compose(org_id, body.profile_id, created_by=user.id)
    await db.commit()
    return DataResponse(data=DraftResponse.model_validate(draft))


# ── Draft management ──────────────────────────────────────


@router.get(
    "/orgs/{org_id}/drafts",
    response_model=ListResponse[DraftResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_drafts(
    org_id: str,
    draft_type: str | None = Query(default=None, max_length=30),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningComposerService(db)
    drafts, total = await svc.list_drafts(org_id, draft_type=draft_type, page=page, per_page=per_page)
    return ListResponse(
        data=[DraftResponse.model_validate(d) for d in drafts],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/orgs/{org_id}/drafts/{draft_id}",
    response_model=DataResponse[DraftResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_draft(
    org_id: str,
    draft_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = LearningComposerService(db)
    draft = await svc.get_draft(draft_id, org_id)
    return DataResponse(data=DraftResponse.model_validate(draft))


@router.patch(
    "/orgs/{org_id}/drafts/{draft_id}",
    response_model=DataResponse[DraftResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def update_draft(
    org_id: str,
    draft_id: str,
    body: UpdateDraftRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = LearningComposerService(db)
    draft = await svc.update_draft(draft_id, org_id, body.remove_entity_ids)
    await db.commit()
    return DataResponse(data=DraftResponse.model_validate(draft))


@router.post(
    "/orgs/{org_id}/drafts/{draft_id}/confirm",
    response_model=DataResponse[ConfirmResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def confirm_draft(
    org_id: str,
    draft_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Human confirmation gate — materializes the draft into a real entity."""
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    learning_svc = LearningComposerService(db)
    draft = await learning_svc.get_draft(draft_id, org_id)
    if draft.draft_type == "learning_path":
        entity = await learning_svc.confirm(draft_id, org_id, confirmed_by=user.id)
    else:
        entity = await ProductionComposerService(db).confirm(
            draft_id, org_id, confirmed_by=user.id
        )
    await db.commit()
    await db.refresh(draft)
    return DataResponse(
        data=ConfirmResponse(
            draft=DraftResponse.model_validate(draft),
            materialized_entity_id=entity.id,
        )
    )


@router.post(
    "/orgs/{org_id}/drafts/{draft_id}/discard",
    response_model=DataResponse[DraftResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def discard_draft(
    org_id: str,
    draft_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = LearningComposerService(db)
    draft = await svc.discard(draft_id, org_id)
    await db.commit()
    return DataResponse(data=DraftResponse.model_validate(draft))


# ── Creator shortlist + assignments ───────────────────────


@router.get(
    "/orgs/{org_id}/projects/{project_id}/creator-shortlist",
    response_model=DataResponse[ShortlistResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def creator_shortlist(
    org_id: str,
    project_id: str,
    profile_id: str = Query(...),
    limit: int = Query(default=10, ge=1, le=25),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = CreatorMatchingService(db)
    run, results, evidence_by_user = await svc.shortlist(
        org_id, project_id, profile_id, created_by=user.id, limit=limit
    )
    await db.commit()

    # Resolve display names (only id/display_name — R9)
    from app.models.user import User as UserModel

    ranked = [r for r in results if r.rank is not None]
    names: dict[str, str] = {}
    if ranked:
        from sqlalchemy import select

        users_r = await db.execute(
            select(UserModel.id, UserModel.display_name).where(
                UserModel.id.in_([r.entity_id for r in ranked])
            )
        )
        names = {row[0]: row[1] for row in users_r.all()}

    return DataResponse(
        data=ShortlistResponse(
            match_run_id=run.id,
            engine_version=run.engine_version,
            results=[
                ShortlistCreator(
                    entity_id=r.entity_id,
                    name=names.get(r.entity_id),
                    rank=r.rank,
                    score=float(r.score) if r.score is not None else None,
                    tier=r.tier,
                    reasons=r.reasons,
                    gaps=r.gaps,
                    evidence=evidence_by_user.get(r.entity_id, {}),
                )
                for r in ranked
            ],
            excluded=[
                {"entity_id": r.entity_id, "failures": r.hard_failures}
                for r in results
                if r.rank is None
            ],
        )
    )


@router.post(
    "/orgs/{org_id}/creator-assignments",
    response_model=DataResponse[AssignmentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def offer_assignment(
    org_id: str,
    body: OfferAssignmentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """A human assigner offers a project to a creator. Never automatic."""
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = CreatorMatchingService(db)
    assignment = await svc.offer_assignment(
        org_id=org_id,
        project_id=body.project_id,
        user_id=body.user_id,
        assigned_by=user.id,
        match_run_id=body.match_run_id,
        override_reason=body.override_reason,
    )
    await db.commit()
    return DataResponse(data=AssignmentResponse.model_validate(assignment))


@router.post(
    "/orgs/{org_id}/creator-assignments/{assignment_id}/respond",
    response_model=DataResponse[AssignmentResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def respond_assignment(
    org_id: str,
    assignment_id: str,
    body: RespondRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Only the offered creator can accept/decline."""
    await require_org_member(org_id, user, db)
    svc = CreatorMatchingService(db)
    assignment = await svc.respond_assignment(
        assignment_id, org_id, user_id=user.id, accept=body.accept
    )
    await db.commit()
    return DataResponse(data=AssignmentResponse.model_validate(assignment))


@router.get(
    "/orgs/{org_id}/creator-assignments",
    response_model=DataResponse[list[AssignmentResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_assignments(
    org_id: str,
    project_id: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = CreatorMatchingService(db)
    assignments = await svc.list_assignments(org_id, project_id=project_id)
    return DataResponse(data=[AssignmentResponse.model_validate(a) for a in assignments])
