"""Workflow Pack management endpoints (ADR-010)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.workflow_pack import (
    CreateWorkflowPackRequest,
    PublishWorkflowReleaseRequest,
    RejectPackRequest,
    UpdateDefinitionRequest,
    UpdateWorkflowPackRequest,
    ValidateDefinitionResponse,
    ValidationErrorItem,
    WorkflowPackDetailResponse,
    WorkflowPackResponse,
    WorkflowReleaseResponse,
)
from app.services.workflow_pack import WorkflowPackService

router = APIRouter(tags=["Workflow Packs"])

WRITE_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


@router.post(
    "/orgs/{org_id}/workflow-packs",
    response_model=DataResponse[WorkflowPackResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def create_workflow_pack(
    org_id: str,
    body: CreateWorkflowPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowPackService(db)
    pack = await svc.create_pack(
        org_id,
        user.id,
        name=body.name,
        summary=body.summary,
        description=body.description,
        workflow_type=body.workflow_type,
        scenario_tags=body.scenario_tags,
        tool_tags=body.tool_tags,
        difficulty=body.difficulty,
        language=body.language,
        provenance=body.provenance,
    )
    await db.commit()
    return DataResponse(data=WorkflowPackResponse.model_validate(pack))


@router.get(
    "/orgs/{org_id}/workflow-packs",
    response_model=ListResponse[WorkflowPackResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_workflow_packs(
    org_id: str,
    status: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowPackService(db)
    packs, total = await svc.list_packs(org_id, status=status, page=page, per_page=per_page)
    return ListResponse(
        data=[WorkflowPackResponse.model_validate(p) for p in packs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/orgs/{org_id}/workflow-packs/{pack_id}",
    response_model=DataResponse[WorkflowPackDetailResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_workflow_pack(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowPackService(db)
    pack = await svc.get_pack(pack_id, org_id)
    return DataResponse(data=WorkflowPackDetailResponse.model_validate(pack))


@router.put(
    "/orgs/{org_id}/workflow-packs/{pack_id}",
    response_model=DataResponse[WorkflowPackResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def update_workflow_pack(
    org_id: str,
    pack_id: str,
    body: UpdateWorkflowPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowPackService(db)
    fields = body.model_dump(exclude_unset=True)
    pack = await svc.update_pack(pack_id, org_id, **fields)
    await db.commit()
    return DataResponse(data=WorkflowPackResponse.model_validate(pack))


@router.delete(
    "/orgs/{org_id}/workflow-packs/{pack_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def delete_workflow_pack(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WorkflowPackService(db)
    await svc.delete_pack(pack_id, org_id)
    await db.commit()


# ── Definition ────────────────────────────────────────────


@router.put(
    "/orgs/{org_id}/workflow-packs/{pack_id}/definition",
    response_model=DataResponse[WorkflowPackDetailResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def update_definition(
    org_id: str,
    pack_id: str,
    body: UpdateDefinitionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowPackService(db)
    pack = await svc.update_definition(pack_id, org_id, body.definition)
    await db.commit()
    return DataResponse(data=WorkflowPackDetailResponse.model_validate(pack))


@router.post(
    "/orgs/{org_id}/workflow-packs/validate",
    response_model=DataResponse[ValidateDefinitionResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def validate_definition_endpoint(
    org_id: str,
    body: UpdateDefinitionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dry-run validation for the editor — returns errors without persisting."""
    await require_org_member(org_id, user, db)
    svc = WorkflowPackService(db)
    errors = await svc.validate_pack_definition(body.definition)
    return DataResponse(
        data=ValidateDefinitionResponse(
            valid=not errors,
            errors=[ValidationErrorItem(**e) for e in errors],
        )
    )


# ── Releases ──────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/workflow-packs/{pack_id}/releases",
    response_model=DataResponse[WorkflowReleaseResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def publish_release(
    org_id: str,
    pack_id: str,
    body: PublishWorkflowReleaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowPackService(db)
    release = await svc.publish_release(
        pack_id,
        org_id,
        version=body.version,
        changelog=body.changelog,
        released_by=user.id,
        dependencies=body.dependencies,
    )
    await db.commit()
    return DataResponse(data=WorkflowReleaseResponse.model_validate(release))


@router.get(
    "/orgs/{org_id}/workflow-packs/{pack_id}/releases",
    response_model=DataResponse[list[WorkflowReleaseResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_releases(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowPackService(db)
    releases = await svc.list_releases(pack_id, org_id)
    return DataResponse(data=[WorkflowReleaseResponse.model_validate(r) for r in releases])


# ── Approval workflow ─────────────────────────────────────


@router.post(
    "/orgs/{org_id}/workflow-packs/{pack_id}/submit-review",
    response_model=DataResponse[WorkflowPackResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def submit_for_review(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowPackService(db)
    pack = await svc.submit_for_review(pack_id, org_id)
    await db.commit()
    return DataResponse(data=WorkflowPackResponse.model_validate(pack))


@router.post(
    "/orgs/{org_id}/workflow-packs/{pack_id}/approve",
    response_model=DataResponse[WorkflowPackResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def approve_pack(
    org_id: str,
    pack_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WorkflowPackService(db)
    pack = await svc.approve_pack(pack_id, org_id)
    await db.commit()
    return DataResponse(data=WorkflowPackResponse.model_validate(pack))


@router.post(
    "/orgs/{org_id}/workflow-packs/{pack_id}/reject",
    response_model=DataResponse[WorkflowPackResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def reject_pack(
    org_id: str,
    pack_id: str,
    body: RejectPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WorkflowPackService(db)
    pack = await svc.reject_pack(pack_id, org_id, reason=body.reason)
    await db.commit()
    return DataResponse(data=WorkflowPackResponse.model_validate(pack))
