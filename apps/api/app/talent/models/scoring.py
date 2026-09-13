"""Capability score snapshots — historical scoring audit trail (ADR-015 D3).

Point-in-time snapshots of multi-dimensional capability scores, enabling:
  - Longitudinal progress tracking
  - Scoring version audit trail
  - Velocity computation from historical data
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class CapabilityScoreSnapshot(Base):
    """Point-in-time snapshot of a user's capability score."""

    __tablename__ = "capability_score_snapshots"

    id: Mapped[str] = ulid_pk()
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE")
    )
    capability_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("capabilities.id", ondelete="CASCADE")
    )

    # Multi-dimensional scores (all 0.0–1.0)
    score: Mapped[float] = mapped_column(Numeric(5, 4))  # composite
    depth: Mapped[float] = mapped_column(Numeric(5, 4))
    breadth: Mapped[float] = mapped_column(Numeric(5, 4))
    recency: Mapped[float] = mapped_column(Numeric(5, 4))
    velocity: Mapped[float] = mapped_column(Numeric(5, 4))
    confidence: Mapped[float] = mapped_column(Numeric(5, 4))

    level: Mapped[int] = mapped_column(Integer)
    evidence_count: Mapped[int] = mapped_column(Integer)

    # Denormalized verification breakdown for audit
    verification_mix: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")

    # Algorithm version that produced this snapshot
    scoring_version: Mapped[str] = mapped_column(String(20))

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: __import__("datetime").datetime.now(__import__("datetime").UTC),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_score_snap_user", "user_id"),
        Index("ix_score_snap_user_cap", "user_id", "capability_id"),
        Index("ix_score_snap_computed", "computed_at"),
    )
