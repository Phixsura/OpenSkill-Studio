"""Region, Cell & Service Infrastructure models (ADR-018 Parts A, B, D).

Multi-region deployment, workload routing, and observability fabric.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class RegionStatus(str, enum.Enum):
    ACTIVE = "active"
    DRAINING = "draining"
    STANDBY = "standby"
    DISABLED = "disabled"


class CellStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    OFFLINE = "offline"


class ServiceStatus(str, enum.Enum):
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    DEPLOYING = "deploying"
    FAILED = "failed"


# ── Models ───────────────────────────────────────────────────────────


class DeploymentRegion(Base):
    __tablename__ = "ops_deployment_regions"
    __table_args__ = (
        Index("uq_ops_region_code", "code", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    code: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g. us-east-1, eu-west-1
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(40), nullable=False)  # aws, gcp, azure
    status: Mapped[RegionStatus] = mapped_column(
        Enum(RegionStatus, name="ops_region_status", create_constraint=True),
        nullable=False, default=RegionStatus.ACTIVE,
    )
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RuntimeCell(Base):
    __tablename__ = "ops_runtime_cells"
    __table_args__ = (
        Index("ix_ops_cell_region", "region_id"),
        Index("ix_ops_cell_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    region_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("ops_deployment_regions.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[CellStatus] = mapped_column(
        Enum(CellStatus, name="ops_cell_status", create_constraint=True),
        nullable=False, default=CellStatus.HEALTHY,
    )
    capacity: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    current_load: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    tenant_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list, server_default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ServiceInstance(Base):
    __tablename__ = "ops_service_instances"
    __table_args__ = (
        Index("ix_ops_service_cell", "cell_id"),
        Index("ix_ops_service_name", "service_name"),
    )

    id: Mapped[str] = ulid_pk()
    cell_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("ops_runtime_cells.id", ondelete="CASCADE"), nullable=False
    )
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus, name="ops_service_status", create_constraint=True),
        nullable=False, default=ServiceStatus.RUNNING,
    )
    endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    health_check_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RoutingRule(Base):
    """Multi-region routing rules for workload placement."""

    __tablename__ = "ops_routing_rules"
    __table_args__ = (
        Index("ix_ops_routing_tenant", "tenant_id"),
    )

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tenant_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # NULL = global
    source_region_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    target_region_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("ops_deployment_regions.id", ondelete="CASCADE"), nullable=False
    )
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MetricSample(Base):
    """Observability metric samples — append-only."""

    __tablename__ = "ops_metric_samples"
    __table_args__ = (
        Index("ix_ops_metric_name_time", "metric_name", "sampled_at"),
        Index("ix_ops_metric_source", "source_type", "source_id"),
    )

    id: Mapped[str] = ulid_pk()
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)  # region, cell, service
    source_id: Mapped[str] = mapped_column(String(26), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    labels: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    sampled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
