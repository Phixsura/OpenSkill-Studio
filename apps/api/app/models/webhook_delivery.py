"""Webhook delivery log for developer apps."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class AppWebhookDelivery(Base):
    __tablename__ = "app_webhook_deliveries"
    __table_args__ = (
        Index("ix_app_wh_delivery_app", "app_id", "created_at"),
        Index("ix_app_wh_delivery_install", "installation_id"),
        Index("ix_app_wh_delivery_status", "status"),
    )

    id: Mapped[str] = ulid_pk()
    app_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False
    )
    installation_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("app_installations.id", ondelete="SET NULL")
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="webhook_delivery_status", create_constraint=True),
        default=DeliveryStatus.PENDING,
    )
    http_status: Mapped[int | None] = mapped_column(Integer)
    attempt: Mapped[int] = mapped_column(Integer, default=1)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
