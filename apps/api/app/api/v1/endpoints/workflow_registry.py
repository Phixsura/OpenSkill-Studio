"""Public workflow-pack registry endpoints (no auth — mirror registry.py)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.rate_limit import rate_limit
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.workflow_pack import (
    PublicWorkflowPackResponse,
    PublicWorkflowReleaseResponse,
    WorkflowPreviewResponse,
)
from app.services.workflow_registry import WorkflowRegistryService

router = APIRouter(tags=["Workflow Registry"])


@router.get(
    "/registry/workflow-packs",
    response_model=ListResponse[PublicWorkflowPackResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def search_workflow_packs(
    search: str | None = Query(default=None, max_length=200),
    scenario: str | None = Query(default=None, max_length=50),
    tool: str | None = Query(default=None, max_length=50),
    capability: str | None = Query(default=None, max_length=64),
    workflow_type: str | None = Query(default=None, max_length=50),
    input_type: str | None = Query(default=None, max_length=20),
    output_type: str | None = Query(default=None, max_length=20),
    sort: str = Query(default="newest", max_length=20),
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    svc = WorkflowRegistryService(db)
    packs, total = await svc.search_packs(
        search=search,
        scenario=scenario,
        tool=tool,
        capability=capability,
        workflow_type=workflow_type,
        input_type=input_type,
        output_type=output_type,
        sort=sort,
        page=page,
        per_page=per_page,
    )
    return ListResponse(
        data=[PublicWorkflowPackResponse.model_validate(p) for p in packs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/registry/workflow-packs/{pack_id}",
    response_model=DataResponse[PublicWorkflowPackResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_workflow_pack(
    pack_id: str,
    db: AsyncSession = Depends(get_db),
):
    svc = WorkflowRegistryService(db)
    pack = await svc.get_public_pack(pack_id)
    return DataResponse(data=PublicWorkflowPackResponse.model_validate(pack))


@router.get(
    "/registry/workflow-packs/{pack_id}/releases",
    response_model=DataResponse[list[PublicWorkflowReleaseResponse]],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def list_workflow_releases(
    pack_id: str,
    db: AsyncSession = Depends(get_db),
):
    svc = WorkflowRegistryService(db)
    releases = await svc.get_public_releases(pack_id)
    return DataResponse(data=[PublicWorkflowReleaseResponse.model_validate(r) for r in releases])


@router.get(
    "/registry/workflow-packs/{pack_id}/preview",
    response_model=DataResponse[WorkflowPreviewResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_workflow_preview(
    pack_id: str,
    db: AsyncSession = Depends(get_db),
):
    svc = WorkflowRegistryService(db)
    preview = await svc.get_pack_preview(pack_id)
    return DataResponse(data=WorkflowPreviewResponse(**preview))
