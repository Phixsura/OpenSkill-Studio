"""Sandbox execution endpoints — trigger and monitor sandboxed app functions."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse
from app.services import developer as dev_svc
from app.services.sandbox import sandbox_manager

router = APIRouter(tags=["App Sandbox"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


class ExecuteFunctionRequest(BaseModel):
    function_name: str
    payload: dict = {}
    timeout_seconds: int = 30
    memory_mb: int = 128


class SandboxExecutionResult(BaseModel):
    success: bool
    output: dict | None = None
    logs: list[dict] = []
    duration_ms: int = 0
    error: str | None = None


@router.post(
    "/orgs/{org_id}/apps/installations/{installation_id}/execute",
    response_model=DataResponse[SandboxExecutionResult],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def execute_function(
    org_id: str,
    installation_id: str,
    body: ExecuteFunctionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Execute a function in an app's sandboxed runtime."""
    await require_org_member(org_id, user, db, *ADMIN_ROLES)

    installation = await dev_svc.get_installation(db, installation_id)
    if installation.org_id != org_id:
        raise dev_svc.InstallationNotFoundError()

    result = await sandbox_manager.execute(
        db,
        installation_id=installation_id,
        app_version_id=installation.app_version_id,
        function_name=body.function_name,
        payload=body.payload,
        trigger_type="manual",
        timeout_seconds=body.timeout_seconds,
        memory_mb=body.memory_mb,
    )
    await db.commit()

    return DataResponse(
        data=SandboxExecutionResult(
            success=result.success,
            output=result.output,
            logs=result.logs,
            duration_ms=result.duration_ms,
            error=result.error,
        )
    )
