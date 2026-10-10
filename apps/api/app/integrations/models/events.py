"""Integration event mesh (ADR-018 §12).

intg_events is the append-only canonical event log (CloudEvents 1.0 fields);
the row id doubles as the CloudEvents ``id`` and the idempotency key at every
hop (receivers dedupe on webhook-id, which is this ULID). Deliveries fan out
per matching webhook subscription; attempts are the per-try audit trail.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

# Svix-style retry ladder (§12.2): seconds after the PREVIOUS attempt.
# Attempt 1 fires immediately on fan-out; offsets[i] schedules attempt i+2.
RETRY_OFFSETS_S = [5, 300, 1800, 7200, 18000, 36000, 36000]
MAX_ATTEMPTS = len(RETRY_OFFSETS_S) + 1  # 8 total

DELIVERY_STATUSES = frozenset({"pending", "delivering", "succeeded", "exhausted", "cancelled"})

# Fabric-internal event types are logged + queryable but fan out ONLY to
# subscriptions naming the exact type — a wildcard must not route
# integration.delivery.exhausted back into the endpoint that is failing
# (exhaustion cascade).
INTERNAL_EVENT_PREFIX = "integration."

# Initial canonical catalog (issue Part F). Emitters pass the bare name; the
# facade prefixes the reverse-DNS namespace + version.
EVENT_NAMESPACE = "com.openskill."


class IntegrationEvent(Base):
    __tablename__ = "intg_events"
    __table_args__ = (Index("ix_intg_events_org_type_time", "org_id", "type", "time"),)

    id: Mapped[str] = ulid_pk()  # CloudEvents id
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    dataschema: Mapped[str | None] = mapped_column(String(200), nullable=True)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")


class EventDelivery(Base):
    __tablename__ = "intg_event_deliveries"
    __table_args__ = (
        # Fan-out idempotency: re-running the outbox handler can never create
        # a second ORIGINAL delivery for the same (event, subscription).
        # Partial — replays (replay_of set) are deliberate extra deliveries.
        Index(
            "uq_intg_delivery_event_sub",
            "event_id",
            "subscription_id",
            unique=True,
            postgresql_where="replay_of IS NULL",
        ),
        Index("ix_intg_delivery_sub_status", "subscription_id", "status", "created_at"),
    )

    id: Mapped[str] = ulid_pk()
    event_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_events.id", ondelete="CASCADE"), nullable=False
    )
    subscription_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Replay lineage: a replayed delivery points at the one it clones.
    replay_of: Mapped[str | None] = mapped_column(String(26), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DeliveryAttempt(Base):
    __tablename__ = "intg_delivery_attempts"
    __table_args__ = (Index("ix_intg_attempts_delivery", "delivery_id", "attempted_at"),)

    id: Mapped[str] = ulid_pk()
    delivery_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_event_deliveries.id", ondelete="CASCADE"), nullable=False
    )
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(String(200), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
