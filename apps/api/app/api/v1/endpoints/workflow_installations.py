"""Workflow pack installation endpoints (ADR-010)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.workflow_pack import (
    ConfirmBindingRequest,
    InstallDiffResponse,
    InstallWorkflowPackRequest,
    StepBindingResponse,
    UpgradeInstallationRequest,
    WorkflowInstallationResponse,
)
from app.services.workflow_installation import WorkflowInstallationService

router = APIRouter(tags=["Workflow Installations"])

WRITE_ROLES = (OrgRole.OWNER, OrgRole.ADMIN, OrgRole.INSTRUCTOR)
ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


@router.post(
    "/orgs/{org_id}/workflow-installations",
    response_model=DataResponse[WorkflowInstallationResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(20, 60))],
)
async def install_workflow_pack(
    org_id: str,
    body: InstallWorkflowPackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowInstallationService(db)
    install = await svc.install(
        org_id=org_id, pack_id=body.pack_id, version=body.version, installed_by=user.id
    )
    await db.commit()
    return DataResponse(data=WorkflowInstallationResponse.model_validate(install))


@router.get(
    "/orgs/{org_id}/workflow-installations",
    response_model=ListResponse[WorkflowInstallationResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_installations(
    org_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowInstallationService(db)
    installs, total = await svc.list_installations(org_id, page=page, per_page=per_page)
    return ListResponse(
        data=[WorkflowInstallationResponse.model_validate(i) for i in installs],
        meta=PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=page * per_page < total
        ),
    )


@router.get(
    "/orgs/{org_id}/workflow-installations/{installation_id}",
    response_model=DataResponse[WorkflowInstallationResponse],
    dependencies=[Depends(rate_limit(60, 60))],
)
async def get_installation(
    org_id: str,
    installation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowInstallationService(db)
    install = await svc.get_installation(installation_id, org_id)
    detail = WorkflowInstallationResponse.model_validate(install)
    # Effective input schema for the run form (works for private packs too)
    detail.input_schema = await svc.get_input_schema(install)
    return DataResponse(data=detail)


@router.post(
    "/orgs/{org_id}/workflow-installations/{installation_id}/upgrade",
    response_model=DataResponse[WorkflowInstallationResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def upgrade_installation(
    org_id: str,
    installation_id: str,
    body: UpgradeInstallationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upgrade OR rollback — any released version is a valid target."""
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowInstallationService(db)
    install = await svc.upgrade(installation_id, org_id, target_version=body.version)
    await db.commit()
    return DataResponse(data=WorkflowInstallationResponse.model_validate(install))


@router.post(
    "/orgs/{org_id}/workflow-installations/{installation_id}/fork",
    response_model=DataResponse[WorkflowInstallationResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def fork_installation(
    org_id: str,
    installation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *WRITE_ROLES)
    svc = WorkflowInstallationService(db)
    install = await svc.fork(installation_id, org_id)
    await db.commit()
    return DataResponse(data=WorkflowInstallationResponse.model_validate(install))


@router.delete(
    "/orgs/{org_id}/workflow-installations/{installation_id}",
    status_code=204,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def remove_installation(
    org_id: str,
    installation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WorkflowInstallationService(db)
    await svc.remove(installation_id, org_id)
    await db.commit()


@router.get(
    "/orgs/{org_id}/workflow-installations/{installation_id}/bindings",
    response_model=DataResponse[list[StepBindingResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_bindings(
    org_id: str,
    installation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowInstallationService(db)
    bindings = await svc.list_bindings(installation_id, org_id)
    return DataResponse(data=[StepBindingResponse.model_validate(b) for b in bindings])


@router.put(
    "/orgs/{org_id}/workflow-installations/{installation_id}/bindings/{step_id}",
    response_model=DataResponse[StepBindingResponse],
    dependencies=[Depends(rate_limit(20, 60))],
)
async def confirm_binding(
    org_id: str,
    installation_id: str,
    step_id: str,
    body: ConfirmBindingRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    svc = WorkflowInstallationService(db)
    binding = await svc.confirm_binding(
        installation_id,
        org_id,
        step_id=step_id,
        offering_id=body.offering_id,
        binding_mode=body.binding_mode,
        confirmed_by=user.id,
    )
    await db.commit()
    return DataResponse(data=StepBindingResponse.model_validate(binding))


@router.get(
    "/orgs/{org_id}/workflow-installations/{installation_id}/diff",
    response_model=DataResponse[InstallDiffResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def compute_diff(
    org_id: str,
    installation_id: str,
    to: str = Query(..., max_length=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    svc = WorkflowInstallationService(db)
    diff = await svc.compute_diff(installation_id, org_id, to_version=to)
    return DataResponse(data=InstallDiffResponse(**diff))
