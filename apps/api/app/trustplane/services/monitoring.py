"""Monitoring & Incidents service (ADR-017 Parts I, J).

Monitor CRUD, alert lifecycle, incident lifecycle with status transitions,
and incident action tracking.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.incidents import (
    ActionStatus,
    ActionType,
    IncidentAction,
    IncidentSeverity,
    IncidentStatus,
    TrustIncident,
)
from app.trustplane.models.inventory import AISystem
from app.trustplane.models.monitoring import (
    AlertSeverity,
    AlertStatus,
    MonitorAlert,
    MonitorStatus,
    MonitorType,
    TrustMonitor,
)
from app.trustplane.services.audit import record_trust_audit
from app.trustplane.services.inventory import SystemNotFoundError

# ── Incident status transitions ──────────────────────────────────────

INCIDENT_TRANSITIONS: dict[IncidentStatus, set[IncidentStatus]] = {
    IncidentStatus.REPORTED: {IncidentStatus.TRIAGING, IncidentStatus.CONTAINED},
    IncidentStatus.TRIAGING: {IncidentStatus.CONTAINED, IncidentStatus.INVESTIGATING},
    IncidentStatus.CONTAINED: {IncidentStatus.INVESTIGATING},
    IncidentStatus.INVESTIGATING: {IncidentStatus.REMEDIATING, IncidentStatus.CONTAINED},
    IncidentStatus.REMEDIATING: {IncidentStatus.VALIDATING},
    IncidentStatus.VALIDATING: {IncidentStatus.CLOSED, IncidentStatus.REMEDIATING},
    IncidentStatus.CLOSED: set(),
}


# ── Errors ───────────────────────────────────────────────────────────


class MonitorNotFoundError(AppError):
    def __init__(self):
        super().__init__("MONITOR_NOT_FOUND", "Monitor not found", 404)


class AlertNotFoundError(AppError):
    def __init__(self):
        super().__init__("ALERT_NOT_FOUND", "Alert not found", 404)


class IncidentNotFoundError(AppError):
    def __init__(self):
        super().__init__("INCIDENT_NOT_FOUND", "Incident not found", 404)


class IncidentInvalidTransitionError(AppError):
    def __init__(self, current: str, target: str):
        super().__init__(
            "INCIDENT_INVALID_TRANSITION",
            f"Cannot transition incident from '{current}' to '{target}'",
            422,
        )


class ActionNotFoundError(AppError):
    def __init__(self):
        super().__init__("ACTION_NOT_FOUND", "Incident action not found", 404)


# ── Monitor CRUD ─────────────────────────────────────────────────────


async def create_monitor(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    name: str,
    monitor_type: str,
    config: dict,
    system_id: str | None = None,
    description: str | None = None,
    alert_severity: str = "warning",
    check_interval_minutes: int = 60,
) -> TrustMonitor:
    if system_id:
        r = await db.execute(
            select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id)
        )
        if r.scalar_one_or_none() is None:
            raise SystemNotFoundError()

    monitor = TrustMonitor(
        org_id=org_id,
        system_id=system_id,
        name=name,
        description=description,
        monitor_type=MonitorType(monitor_type),
        status=MonitorStatus.ACTIVE,
        config=config,
        alert_severity=AlertSeverity(alert_severity),
        check_interval_minutes=check_interval_minutes,
        created_by=user_id,
    )
    db.add(monitor)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="monitor.created",
        target_type="trust_monitor",
        target_id=monitor.id,
        after={"name": name, "monitor_type": monitor_type},
    )
    return monitor


async def get_monitor(db: AsyncSession, monitor_id: str, org_id: str) -> TrustMonitor:
    result = await db.execute(
        select(TrustMonitor).where(TrustMonitor.id == monitor_id, TrustMonitor.org_id == org_id)
    )
    monitor = result.scalar_one_or_none()
    if monitor is None:
        raise MonitorNotFoundError()
    return monitor


async def list_monitors(
    db: AsyncSession,
    org_id: str,
    *,
    monitor_type: str | None = None,
    system_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[TrustMonitor], int]:
    base = select(TrustMonitor).where(TrustMonitor.org_id == org_id)
    count_base = select(func.count()).select_from(TrustMonitor).where(TrustMonitor.org_id == org_id)

    if monitor_type:
        base = base.where(TrustMonitor.monitor_type == monitor_type)
        count_base = count_base.where(TrustMonitor.monitor_type == monitor_type)
    if system_id:
        base = base.where(TrustMonitor.system_id == system_id)
        count_base = count_base.where(TrustMonitor.system_id == system_id)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(TrustMonitor.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Alerts ───────────────────────────────────────────────────────────


async def create_alert(
    db: AsyncSession,
    org_id: str,
    *,
    monitor_id: str,
    title: str,
    severity: str,
    system_id: str | None = None,
    detail: str | None = None,
    metric_value: dict | None = None,
    threshold: dict | None = None,
) -> MonitorAlert:
    alert = MonitorAlert(
        org_id=org_id,
        monitor_id=monitor_id,
        system_id=system_id,
        severity=AlertSeverity(severity),
        status=AlertStatus.OPEN,
        title=title,
        detail=detail,
        metric_value=metric_value,
        threshold=threshold,
    )
    db.add(alert)
    await db.flush()
    return alert


async def acknowledge_alert(
    db: AsyncSession,
    alert_id: str,
    org_id: str,
    user_id: str,
) -> MonitorAlert:
    result = await db.execute(
        select(MonitorAlert).where(MonitorAlert.id == alert_id, MonitorAlert.org_id == org_id)
    )
    alert = result.scalar_one_or_none()
    if alert is None:
        raise AlertNotFoundError()

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by = user_id
    alert.acknowledged_at = datetime.now(UTC)
    await db.flush()
    return alert


async def resolve_alert(
    db: AsyncSession,
    alert_id: str,
    org_id: str,
) -> MonitorAlert:
    result = await db.execute(
        select(MonitorAlert).where(MonitorAlert.id == alert_id, MonitorAlert.org_id == org_id)
    )
    alert = result.scalar_one_or_none()
    if alert is None:
        raise AlertNotFoundError()

    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.now(UTC)
    await db.flush()
    return alert


async def list_alerts(
    db: AsyncSession,
    org_id: str,
    *,
    severity: str | None = None,
    status: str | None = None,
    monitor_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[MonitorAlert], int]:
    base = select(MonitorAlert).where(MonitorAlert.org_id == org_id)
    count_base = select(func.count()).select_from(MonitorAlert).where(MonitorAlert.org_id == org_id)

    if severity:
        base = base.where(MonitorAlert.severity == severity)
        count_base = count_base.where(MonitorAlert.severity == severity)
    if status:
        base = base.where(MonitorAlert.status == status)
        count_base = count_base.where(MonitorAlert.status == status)
    if monitor_id:
        base = base.where(MonitorAlert.monitor_id == monitor_id)
        count_base = count_base.where(MonitorAlert.monitor_id == monitor_id)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(MonitorAlert.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Incidents ────────────────────────────────────────────────────────


async def create_incident(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    title: str,
    severity: str,
    system_id: str | None = None,
    description: str | None = None,
    impact: dict | None = None,
    assigned_to: str | None = None,
) -> TrustIncident:
    if system_id:
        r = await db.execute(
            select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id)
        )
        if r.scalar_one_or_none() is None:
            raise SystemNotFoundError()

    incident = TrustIncident(
        org_id=org_id,
        system_id=system_id,
        title=title,
        description=description,
        severity=IncidentSeverity(severity),
        status=IncidentStatus.REPORTED,
        impact=impact,
        reported_by=user_id,
        assigned_to=assigned_to,
    )
    db.add(incident)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="incident.created",
        target_type="trust_incident",
        target_id=incident.id,
        after={"title": title, "severity": severity},
    )
    return incident


async def get_incident(db: AsyncSession, incident_id: str, org_id: str) -> TrustIncident:
    result = await db.execute(
        select(TrustIncident).where(
            TrustIncident.id == incident_id, TrustIncident.org_id == org_id
        )
    )
    incident = result.scalar_one_or_none()
    if incident is None:
        raise IncidentNotFoundError()
    return incident


async def change_incident_status(
    db: AsyncSession,
    incident_id: str,
    org_id: str,
    user_id: str,
    new_status: str,
) -> TrustIncident:
    incident = await get_incident(db, incident_id, org_id)
    target = IncidentStatus(new_status)
    allowed = INCIDENT_TRANSITIONS.get(incident.status, set())
    if target not in allowed:
        raise IncidentInvalidTransitionError(incident.status.value, target.value)

    old = incident.status.value
    incident.status = target
    now = datetime.now(UTC)
    if target == IncidentStatus.CONTAINED:
        incident.contained_at = now
    elif target == IncidentStatus.CLOSED:
        incident.closed_at = now
        incident.resolved_at = incident.resolved_at or now
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="incident.status_changed",
        target_type="trust_incident",
        target_id=incident_id,
        before={"status": old},
        after={"status": new_status},
    )
    return incident


async def list_incidents(
    db: AsyncSession,
    org_id: str,
    *,
    severity: str | None = None,
    status: str | None = None,
    system_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[TrustIncident], int]:
    base = select(TrustIncident).where(TrustIncident.org_id == org_id)
    count_base = (
        select(func.count()).select_from(TrustIncident).where(TrustIncident.org_id == org_id)
    )

    if severity:
        base = base.where(TrustIncident.severity == severity)
        count_base = count_base.where(TrustIncident.severity == severity)
    if status:
        base = base.where(TrustIncident.status == status)
        count_base = count_base.where(TrustIncident.status == status)
    if system_id:
        base = base.where(TrustIncident.system_id == system_id)
        count_base = count_base.where(TrustIncident.system_id == system_id)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(TrustIncident.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Incident Actions ────────────────────────────────────────────────


async def add_action(
    db: AsyncSession,
    incident_id: str,
    org_id: str,
    user_id: str,
    *,
    action_type: str,
    title: str,
    description: str | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
) -> IncidentAction:
    await get_incident(db, incident_id, org_id)

    action = IncidentAction(
        incident_id=incident_id,
        action_type=ActionType(action_type),
        status=ActionStatus.PENDING,
        title=title,
        description=description,
        target_type=target_type,
        target_id=target_id,
        performed_by=user_id,
    )
    db.add(action)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="incident.action_added",
        target_type="incident_action",
        target_id=action.id,
        after={"incident_id": incident_id, "action_type": action_type, "title": title},
    )
    return action


async def complete_action(
    db: AsyncSession,
    action_id: str,
    incident_id: str,
    org_id: str,
    user_id: str,
    *,
    result: dict | None = None,
) -> IncidentAction:
    await get_incident(db, incident_id, org_id)

    r = await db.execute(
        select(IncidentAction).where(
            IncidentAction.id == action_id,
            IncidentAction.incident_id == incident_id,
        )
    )
    action = r.scalar_one_or_none()
    if action is None:
        raise ActionNotFoundError()

    action.status = ActionStatus.COMPLETED
    action.completed_at = datetime.now(UTC)
    action.result = result
    await db.flush()
    return action


async def list_actions(
    db: AsyncSession,
    incident_id: str,
    org_id: str,
) -> list[IncidentAction]:
    await get_incident(db, incident_id, org_id)
    result = await db.execute(
        select(IncidentAction)
        .where(IncidentAction.incident_id == incident_id)
        .order_by(IncidentAction.created_at)
    )
    return list(result.scalars().all())
