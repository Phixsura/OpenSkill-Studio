"""Webhook endpoint registration models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class WebhookEndpointConfig(Base):
    __tablename__ = "talent_webhook_endpoints"

    def __repr__(self) -> str:
        return f"<WebhookEndpointConfig {self.id}>"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(500))
    secret: Mapped[str] = mapped_column(String(200))
    event_types: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class WebhookDeliveryLog(Base):
    __tablename__ = "talent_webhook_delivery_log"

    def __repr__(self) -> str:
        return f"<WebhookDeliveryLog {self.id}>"

    id: Mapped[str] = ulid_pk()
    endpoint_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("talent_webhook_endpoints.id", ondelete="CASCADE"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(50))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    response_code: Mapped[int | None] = mapped_column(nullable=True)
    attempts: Mapped[int] = mapped_column(default=0)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
