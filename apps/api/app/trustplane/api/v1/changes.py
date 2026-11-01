"""Change Management & Revalidation API (ADR-017 Part K)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.changes import (
    ChangeEventResponse,
    ChangeEventSummaryResponse,
    CreateChangeEventRequest,
)
from app.trustplane.services import changes as changes_svc

router = APIRouter(tags=["Trust — Change Management"])
ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


@router.post("/orgs/{org_id}/trust/changes", response_model=DataResponse[ChangeEventResponse], status_code=201, dependencies=[Depends(rate_limit(10, 60))])
async def create_change_event(org_id: str, body: CreateChangeEventRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    event = await changes_svc.create_change_event(db, org_id, user.id, **body.model_dump(exclude_none=True))
    await db.commit()
    return DataResponse(data=ChangeEventResponse.model_validate(event))


@router.get("/orgs/{org_id}/trust/changes", response_model=ListResponse[ChangeEventSummaryResponse], dependencies=[Depends(rate_limit(30, 60))])
async def list_change_events(org_id: str, system_id: str | None = None, change_type: str | None = None, impact: str | None = None, page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    events, total = await changes_svc.list_change_events(db, org_id, system_id=system_id, change_type=change_type, impact=impact, page=page, per_page=per_page)
    return ListResponse(data=[ChangeEventSummaryResponse.model_validate(e) for e in events], meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total))


@router.get("/orgs/{org_id}/trust/changes/{event_id}", response_model=DataResponse[ChangeEventResponse], dependencies=[Depends(rate_limit(30, 60))])
async def get_change_event(org_id: str, event_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db)
    event = await changes_svc.get_change_event(db, event_id, org_id)
    return DataResponse(data=ChangeEventResponse.model_validate(event))


@router.post("/orgs/{org_id}/trust/changes/{event_id}/revalidate", response_model=DataResponse[ChangeEventResponse], dependencies=[Depends(rate_limit(10, 60))])
async def mark_revalidated(org_id: str, event_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    event = await changes_svc.mark_revalidated(db, event_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=ChangeEventResponse.model_validate(event))
