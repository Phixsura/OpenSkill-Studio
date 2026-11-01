"""Infrastructure service (Issue #46 Parts A, B, D)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.opsplane.models.infrastructure import (
    DeploymentRegion,
    MetricSample,
    RoutingRule,
    RuntimeCell,
    ServiceInstance,
)


class RegionNotFoundError(AppError):
    def __init__(self):
        super().__init__("REGION_NOT_FOUND", "Deployment region not found", 404)


class CellNotFoundError(AppError):
    def __init__(self):
        super().__init__("CELL_NOT_FOUND", "Runtime cell not found", 404)


# ── Regions ──────────────────────────────────────────────────────────


async def create_region(db: AsyncSession, *, code: str, name: str, provider: str, is_primary: bool = False, config: dict | None = None) -> DeploymentRegion:
    region = DeploymentRegion(code=code, name=name, provider=provider, is_primary=is_primary, config=config or {})
    db.add(region)
    await db.flush()
    return region


async def list_regions(db: AsyncSession) -> list[DeploymentRegion]:
    result = await db.execute(select(DeploymentRegion).order_by(DeploymentRegion.code))
    return list(result.scalars().all())


async def get_region(db: AsyncSession, region_id: str) -> DeploymentRegion:
    region = await db.get(DeploymentRegion, region_id)
    if region is None:
        raise RegionNotFoundError()
    return region


# ── Cells ────────────────────────────────────────────────────────────


async def create_cell(db: AsyncSession, *, region_id: str, name: str, capacity: dict | None = None) -> RuntimeCell:
    await get_region(db, region_id)
    cell = RuntimeCell(region_id=region_id, name=name, capacity=capacity or {})
    db.add(cell)
    await db.flush()
    return cell


async def list_cells(db: AsyncSession, region_id: str | None = None) -> list[RuntimeCell]:
    base = select(RuntimeCell)
    if region_id:
        base = base.where(RuntimeCell.region_id == region_id)
    result = await db.execute(base.order_by(RuntimeCell.name))
    return list(result.scalars().all())


async def get_cell(db: AsyncSession, cell_id: str) -> RuntimeCell:
    cell = await db.get(RuntimeCell, cell_id)
    if cell is None:
        raise CellNotFoundError()
    return cell


# ── Services ─────────────────────────────────────────────────────────


async def register_service(db: AsyncSession, *, cell_id: str, service_name: str, version: str, endpoint: str | None = None, health_check_url: str | None = None) -> ServiceInstance:
    await get_cell(db, cell_id)
    svc = ServiceInstance(cell_id=cell_id, service_name=service_name, version=version, endpoint=endpoint, health_check_url=health_check_url)
    db.add(svc)
    await db.flush()
    return svc


async def list_services(db: AsyncSession, cell_id: str | None = None, service_name: str | None = None) -> list[ServiceInstance]:
    base = select(ServiceInstance)
    if cell_id:
        base = base.where(ServiceInstance.cell_id == cell_id)
    if service_name:
        base = base.where(ServiceInstance.service_name == service_name)
    result = await db.execute(base.order_by(ServiceInstance.service_name))
    return list(result.scalars().all())


# ── Routing ──────────────────────────────────────────────────────────


async def create_routing_rule(db: AsyncSession, *, name: str, target_region_id: str, tenant_id: str | None = None, conditions: dict | None = None, weight: int = 100) -> RoutingRule:
    await get_region(db, target_region_id)
    rule = RoutingRule(name=name, target_region_id=target_region_id, tenant_id=tenant_id, conditions=conditions or {}, weight=weight)
    db.add(rule)
    await db.flush()
    return rule


async def list_routing_rules(db: AsyncSession, tenant_id: str | None = None) -> list[RoutingRule]:
    base = select(RoutingRule).where(RoutingRule.is_active.is_(True))
    if tenant_id:
        base = base.where((RoutingRule.tenant_id == tenant_id) | (RoutingRule.tenant_id.is_(None)))
    result = await db.execute(base.order_by(RoutingRule.weight.desc()))
    return list(result.scalars().all())


# ── Metrics ──────────────────────────────────────────────────────────


async def record_metric(db: AsyncSession, *, metric_name: str, source_type: str, source_id: str, value: float, labels: dict | None = None) -> MetricSample:
    sample = MetricSample(metric_name=metric_name, source_type=source_type, source_id=source_id, value=value, labels=labels or {})
    db.add(sample)
    await db.flush()
    return sample
