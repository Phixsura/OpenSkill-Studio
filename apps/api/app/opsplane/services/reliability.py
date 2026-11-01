"""Reliability service (Issue #46 Parts C, E, F, I, L)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.opsplane.models.reliability import (
    DetectionRule,
    FailoverRecord,
    OpsIncident,
    OpsIncidentSeverity,
    RecoveryPlan,
    SloDefinition,
)


class SloNotFoundError(AppError):
    def __init__(self):
        super().__init__("SLO_NOT_FOUND", "SLO definition not found", 404)


class IncidentNotFoundError(AppError):
    def __init__(self):
        super().__init__("OPS_INCIDENT_NOT_FOUND", "Operations incident not found", 404)


# ── SLOs ─────────────────────────────────────────────────────────────


async def create_slo(db: AsyncSession, *, name: str, sli_metric: str, target_value: str, target_unit: str, error_budget_total: str, org_id: str | None = None, description: str | None = None, window_days: int = 30) -> SloDefinition:
    slo = SloDefinition(
        org_id=org_id, name=name, description=description, sli_metric=sli_metric,
        target_value=Decimal(target_value), target_unit=target_unit,
        window_days=window_days, error_budget_total=Decimal(error_budget_total),
        error_budget_remaining=Decimal(error_budget_total),
    )
    db.add(slo)
    await db.flush()
    return slo


async def list_slos(db: AsyncSession, org_id: str | None = None) -> list[SloDefinition]:
    base = select(SloDefinition)
    if org_id:
        base = base.where((SloDefinition.org_id == org_id) | (SloDefinition.org_id.is_(None)))
    result = await db.execute(base.order_by(SloDefinition.name))
    return list(result.scalars().all())


async def get_slo(db: AsyncSession, slo_id: str) -> SloDefinition:
    slo = await db.get(SloDefinition, slo_id)
    if slo is None:
        raise SloNotFoundError()
    return slo


# ── Incidents ────────────────────────────────────────────────────────


async def create_incident(db: AsyncSession, *, title: str, severity: str, description: str | None = None, region_id: str | None = None, detection_source: str = "manual") -> OpsIncident:
    incident = OpsIncident(
        title=title, description=description,
        severity=OpsIncidentSeverity(severity),
        detection_source=detection_source, region_id=region_id,
    )
    db.add(incident)
    await db.flush()
    return incident


async def list_incidents(db: AsyncSession, *, severity: str | None = None, status: str | None = None, page: int = 1, per_page: int = 20) -> tuple[list[OpsIncident], int]:
    base = select(OpsIncident)
    count_q = select(func.count()).select_from(OpsIncident)
    if severity:
        base = base.where(OpsIncident.severity == severity)
        count_q = count_q.where(OpsIncident.severity == severity)
    if status:
        base = base.where(OpsIncident.status == status)
        count_q = count_q.where(OpsIncident.status == status)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(base.order_by(OpsIncident.detected_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def get_incident(db: AsyncSession, incident_id: str) -> OpsIncident:
    incident = await db.get(OpsIncident, incident_id)
    if incident is None:
        raise IncidentNotFoundError()
    return incident


# ── Detection Rules ──────────────────────────────────────────────────


async def create_detection_rule(db: AsyncSession, *, name: str, rule_type: str, conditions: dict, severity: str, description: str | None = None, cooldown_minutes: int = 15) -> DetectionRule:
    rule = DetectionRule(name=name, description=description, rule_type=rule_type, conditions=conditions, severity=OpsIncidentSeverity(severity), cooldown_minutes=cooldown_minutes)
    db.add(rule)
    await db.flush()
    return rule


async def list_detection_rules(db: AsyncSession, status: str | None = None) -> list[DetectionRule]:
    base = select(DetectionRule)
    if status:
        base = base.where(DetectionRule.status == status)
    result = await db.execute(base.order_by(DetectionRule.name))
    return list(result.scalars().all())


# ── Failover ─────────────────────────────────────────────────────────


async def create_failover(db: AsyncSession, *, source_region_id: str, target_region_id: str, trigger: str, incident_id: str | None = None, initiated_by: str | None = None) -> FailoverRecord:
    record = FailoverRecord(
        source_region_id=source_region_id, target_region_id=target_region_id,
        trigger=trigger, incident_id=incident_id, initiated_by=initiated_by,
    )
    db.add(record)
    await db.flush()
    return record


async def list_failovers(db: AsyncSession, page: int = 1, per_page: int = 20) -> tuple[list[FailoverRecord], int]:
    total = (await db.execute(select(func.count()).select_from(FailoverRecord))).scalar() or 0
    result = await db.execute(select(FailoverRecord).order_by(FailoverRecord.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


# ── Recovery Plans ───────────────────────────────────────────────────


async def create_recovery_plan(db: AsyncSession, *, name: str, scenario: str, steps: list, description: str | None = None, rto_minutes: int | None = None, rpo_minutes: int | None = None) -> RecoveryPlan:
    plan = RecoveryPlan(name=name, description=description, scenario=scenario, steps=steps, rto_minutes=rto_minutes, rpo_minutes=rpo_minutes)
    db.add(plan)
    await db.flush()
    return plan


async def list_recovery_plans(db: AsyncSession) -> list[RecoveryPlan]:
    result = await db.execute(select(RecoveryPlan).order_by(RecoveryPlan.name))
    return list(result.scalars().all())
