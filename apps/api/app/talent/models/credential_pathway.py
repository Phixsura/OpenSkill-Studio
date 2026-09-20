"""Credential pathway model — stackable credentials (N2).

A pathway defines a set of prerequisite credentials that, when earned,
unlock a higher-level pathway credential. Supports "N of M" completion
(e.g. earn 3 of 5 elective credentials to unlock the master credential).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

PATHWAY_STATUSES = frozenset({"active", "archived"})


class CredentialPathway(Base):
    __tablename__ = "talent_credential_pathways"


    def __repr__(self) -> str:
        return f"<CredentialPathway {self.id}>"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pathway_credential_type: Mapped[str] = mapped_column(String(100))
    # List of credential_type strings that are prerequisites
    prerequisite_credential_types: Mapped[list] = mapped_column(
        JSONB, default=list, server_default="[]"
    )
    # How many prerequisites are required (default: all)
    prerequisite_count: Mapped[int] = mapped_column(Integer)
    auto_issue: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
