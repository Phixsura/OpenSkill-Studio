"""Roster provisioning endpoint (ADR-018 §6.2)."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.integrations.services.roster import RosterProvisioningService
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse

router = APIRouter(prefix="/orgs/{org_id}/integrations", tags=["Integrations"])


class ProvisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    auto_create_cohorts: bool = True
    jit_users: bool = False
    on_unenroll: str = "remove_membership"


@router.post(
    "/connections/{connection_id}/provision-roster", response_model=DataResponse[dict]
)
async def provision_roster(
    org_id: str,
    connection_id: str,
    body: ProvisionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await require_org_member(org_id, user, db, OrgRole.OWNER, OrgRole.ADMIN)
    report = await RosterProvisioningService(db).provision(
        org_id,
        connection_id,
        actor_id=user.id,
        options=body.model_dump(),
    )
    await db.commit()
    return {"data": report}
