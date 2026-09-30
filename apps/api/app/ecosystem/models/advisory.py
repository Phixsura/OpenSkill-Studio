"""Security advisory registry (ADR-016 §38, Snyk/Dependabot bar)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

ADVISORY_SEVERITIES = frozenset({"low", "medium", "high", "critical"})
ADVISORY_STATUSES = frozenset({"open", "mitigated", "dismissed"})


class SecurityAdvisory(Base):
    """One structured security advisory (CVE/GHSA/vendor bulletin).

    Registration is a curated act: advisories arrive via admin action or
    verified observation, never auto-published from raw scraping. Affected
    entities are RESOLVED on demand from `affected_ref` + `affected_range`
    (version_in_range fails open: unparseable constraints count as affected).
    """

    __tablename__ = "eco_security_advisories"

    id: Mapped[str] = ulid_pk()
    # External identifier: CVE-2026-..., GHSA-..., or vendor bulletin id
    advisory_ref: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    # low | medium | high | critical
    severity: Mapped[str] = mapped_column(String(10))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Catalog kind the ref names (node_package | model_version | ...) — None = any
    affected_kind: Mapped[str | None] = mapped_column(String(30), nullable=True)
    # Name/slug of the affected package/model (matched against canonical_name)
    affected_ref: Mapped[str] = mapped_column(String(300))
    # Version range like '>=2.0 <3.0' / '^1.2' / bare prefix — None = all versions
    affected_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fixed_in: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_observation_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("eco_observations.id", ondelete="SET NULL"), nullable=True
    )
    # open | mitigated | dismissed
    status: Mapped[str] = mapped_column(String(20), default="open", server_default="open")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_eco_advisories_status", "status", "severity"),)
