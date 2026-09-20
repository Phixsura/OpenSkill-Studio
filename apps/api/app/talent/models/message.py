"""In-app messaging models."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ApplicationMessage(Base):
    __tablename__ = "talent_application_messages"

    id: Mapped[str] = ulid_pk()
    application_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("applications.id", ondelete="CASCADE"), index=True
    )
    sender_id: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="CASCADE"))
    sender_role: Mapped[str] = mapped_column(String(20))  # candidate, employer
    message_type: Mapped[str] = mapped_column(String(30), default="text")
    content: Mapped[str] = mapped_column(Text)
    attachments: Mapped[list] = mapped_column(JSONB, default=list, server_default="[]")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
