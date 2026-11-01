"""Monitoring & Incidents API (ADR-017 Phase 5).

Org-scoped endpoints for monitors, alerts, incidents, and incident actions.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_org_member
from app.core.rate_limit import rate_limit
from app.models.organization import OrgRole
from app.models.user import User
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.trustplane.schemas.monitoring import (
    ActionResponse,
    AddActionRequest,
    AlertResponse,
    ChangeIncidentStatusRequest,
    CreateIncidentRequest,
    CreateMonitorRequest,
    IncidentResponse,
    IncidentSummaryResponse,
    MonitorResponse,
    MonitorSummaryResponse,
)
from app.trustplane.services import monitoring as mon_svc

router = APIRouter(tags=["Trust — Monitoring & Incidents"])

ADMIN_ROLES = (OrgRole.OWNER, OrgRole.ADMIN)


# ── Monitors ─────────────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/monitors",
    response_model=DataResponse[MonitorResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_monitor(
    org_id: str,
    body: CreateMonitorRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    monitor = await mon_svc.create_monitor(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=MonitorResponse.model_validate(monitor))


@router.get(
    "/orgs/{org_id}/trust/monitors",
    response_model=ListResponse[MonitorSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_monitors(
    org_id: str,
    monitor_type: str | None = None,
    system_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    monitors, total = await mon_svc.list_monitors(
        db, org_id, monitor_type=monitor_type, system_id=system_id,
        page=page, per_page=per_page,
    )
    return ListResponse(
        data=[MonitorSummaryResponse.model_validate(m) for m in monitors],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/monitors/{monitor_id}",
    response_model=DataResponse[MonitorResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_monitor(
    org_id: str,
    monitor_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    monitor = await mon_svc.get_monitor(db, monitor_id, org_id)
    return DataResponse(data=MonitorResponse.model_validate(monitor))


# ── Alerts ───────────────────────────────────────────────────────────


@router.get(
    "/orgs/{org_id}/trust/alerts",
    response_model=ListResponse[AlertResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_alerts(
    org_id: str,
    severity: str | None = None,
    status: str | None = None,
    monitor_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    alerts, total = await mon_svc.list_alerts(
        db, org_id, severity=severity, status=status, monitor_id=monitor_id,
        page=page, per_page=per_page,
    )
    return ListResponse(
        data=[AlertResponse.model_validate(a) for a in alerts],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.post(
    "/orgs/{org_id}/trust/alerts/{alert_id}/acknowledge",
    response_model=DataResponse[AlertResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def acknowledge_alert(
    org_id: str,
    alert_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    alert = await mon_svc.acknowledge_alert(db, alert_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=AlertResponse.model_validate(alert))


@router.post(
    "/orgs/{org_id}/trust/alerts/{alert_id}/resolve",
    response_model=DataResponse[AlertResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def resolve_alert(
    org_id: str,
    alert_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    alert = await mon_svc.resolve_alert(db, alert_id, org_id)
    await db.commit()
    return DataResponse(data=AlertResponse.model_validate(alert))


# ── Incidents ────────────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/incidents",
    response_model=DataResponse[IncidentResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def create_incident(
    org_id: str,
    body: CreateIncidentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    incident = await mon_svc.create_incident(
        db, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=IncidentResponse.model_validate(incident))


@router.get(
    "/orgs/{org_id}/trust/incidents",
    response_model=ListResponse[IncidentSummaryResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_incidents(
    org_id: str,
    severity: str | None = None,
    status: str | None = None,
    system_id: str | None = None,
    page: int = Query(default=1, ge=1, le=1_000_000),
    per_page: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    incidents, total = await mon_svc.list_incidents(
        db, org_id, severity=severity, status=status,
        system_id=system_id, page=page, per_page=per_page,
    )
    return ListResponse(
        data=[IncidentSummaryResponse.model_validate(i) for i in incidents],
        meta=PaginationMeta(total=total, page=page, per_page=per_page, has_more=(page * per_page) < total),
    )


@router.get(
    "/orgs/{org_id}/trust/incidents/{incident_id}",
    response_model=DataResponse[IncidentResponse],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def get_incident(
    org_id: str,
    incident_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    incident = await mon_svc.get_incident(db, incident_id, org_id)
    return DataResponse(data=IncidentResponse.model_validate(incident))


@router.post(
    "/orgs/{org_id}/trust/incidents/{incident_id}/status",
    response_model=DataResponse[IncidentResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def change_incident_status(
    org_id: str,
    incident_id: str,
    body: ChangeIncidentStatusRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    incident = await mon_svc.change_incident_status(
        db, incident_id, org_id, user.id, body.status
    )
    await db.commit()
    return DataResponse(data=IncidentResponse.model_validate(incident))


# ── Incident Actions ─────────────────────────────────────────────────


@router.post(
    "/orgs/{org_id}/trust/incidents/{incident_id}/actions",
    response_model=DataResponse[ActionResponse],
    status_code=201,
    dependencies=[Depends(rate_limit(10, 60))],
)
async def add_action(
    org_id: str,
    incident_id: str,
    body: AddActionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    action = await mon_svc.add_action(
        db, incident_id, org_id, user.id, **body.model_dump(exclude_none=True)
    )
    await db.commit()
    return DataResponse(data=ActionResponse.model_validate(action))


@router.get(
    "/orgs/{org_id}/trust/incidents/{incident_id}/actions",
    response_model=DataResponse[list[ActionResponse]],
    dependencies=[Depends(rate_limit(30, 60))],
)
async def list_actions(
    org_id: str,
    incident_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db)
    actions = await mon_svc.list_actions(db, incident_id, org_id)
    return DataResponse(data=[ActionResponse.model_validate(a) for a in actions])


@router.post(
    "/orgs/{org_id}/trust/incidents/{incident_id}/actions/{action_id}/complete",
    response_model=DataResponse[ActionResponse],
    dependencies=[Depends(rate_limit(10, 60))],
)
async def complete_action(
    org_id: str,
    incident_id: str,
    action_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_org_member(org_id, user, db, *ADMIN_ROLES)
    action = await mon_svc.complete_action(db, action_id, incident_id, org_id, user.id)
    await db.commit()
    return DataResponse(data=ActionResponse.model_validate(action))
