"""Component draft endpoints (Part K) — draft-only, publish behind approval."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.ecosystem.api.deps import eco_audit, require_platform_admin
from app.ecosystem.schemas import (
    CreateDraftRequest,
    DraftResponse,
    GenerateSkillUpdateDraftRequest,
    GenerateWorkflowDraftRequest,
    UpdateDraftPayloadRequest,
)
from app.ecosystem.services.drafts import DraftService
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/ecosystem/drafts", tags=["Ecosystem — Drafts"])


@router.post("", response_model=DataResponse[DraftResponse], status_code=201)
async def create_draft(
    body: CreateDraftRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    draft = await DraftService(db).create(created_by=user.id, **body.model_dump())
    await db.commit()
    return {"data": draft}


@router.post("/generate/workflow-pack", response_model=DataResponse[DraftResponse], status_code=201)
async def generate_workflow_draft(
    body: GenerateWorkflowDraftRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    draft = await DraftService(db).generate_workflow_pack_draft(
        external_workflow_id=body.external_workflow_id,
        org_id=body.org_id,
        created_by=user.id,
    )
    await db.commit()
    return {"data": draft}


@router.post(
    "/generate/skill-pack-update", response_model=DataResponse[DraftResponse], status_code=201
)
async def generate_skill_update_draft(
    body: GenerateSkillUpdateDraftRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    draft = await DraftService(db).generate_skill_pack_update_draft(
        target_pack_id=body.target_pack_id,
        deprecated_kind=body.deprecated_kind,
        deprecated_id=body.deprecated_id,
        replacement_id=body.replacement_id,
        affected=body.affected,
        created_by=user.id,
    )
    await db.commit()
    return {"data": draft}


@router.get("", response_model=DataResponse[list[DraftResponse]])
async def list_drafts(
    draft_type: str | None = None,
    status: str | None = None,
    org_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {
        "data": await DraftService(db).list(
            draft_type=draft_type, status=status, org_id=org_id, limit=limit, offset=offset
        )
    }


@router.get("/{draft_id}", response_model=DataResponse[DraftResponse])
async def get_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return {"data": await DraftService(db).get(draft_id)}


@router.patch("/{draft_id}", response_model=DataResponse[DraftResponse])
async def update_draft(
    draft_id: str,
    body: UpdateDraftPayloadRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_platform_admin),
):
    draft = await DraftService(db).update_payload(draft_id, payload=body.payload)
    await db.commit()
    return {"data": draft}


async def _transition(draft_id: str, to_status: str, db: AsyncSession, user: User):
    draft = await DraftService(db).transition(draft_id, to_status=to_status, actor_id=user.id)
    await db.commit()
    return {"data": draft}


@router.post("/{draft_id}/submit-review", response_model=DataResponse[DraftResponse])
async def submit_review(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    return await _transition(draft_id, "in_review", db, user)


@router.post("/{draft_id}/approve", response_model=DataResponse[DraftResponse])
async def approve_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    return await _transition(draft_id, "approved", db, user)


@router.post("/{draft_id}/reject", response_model=DataResponse[DraftResponse])
async def reject_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    return await _transition(draft_id, "rejected", db, user)


@router.post("/{draft_id}/publish", response_model=DataResponse[DraftResponse])
async def publish_draft(
    draft_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_platform_admin),
):
    """Second explicit human action — refused unless status is approved."""
    outcome = await _transition(draft_id, "published", db, user)
    await eco_audit(
        db, user, action="eco.draft_published", target_type="eco_component_draft",
        target_id=draft_id,
        after={"published_ref": outcome["data"].published_ref},
    )
    await db.commit()
    return outcome
