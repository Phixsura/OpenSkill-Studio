"""External identity links + ambiguous-match queue (ADR-018 §9).

Links are TENANT-SCOPED and reversible: the same external subject in two
orgs is two rows, never a bridge. Lookup is by the IdP's STABLE subject —
email is snapshotted at link time for audit but never used for
re-resolution (email/UPN changes must not re-link accounts).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

LINK_SOURCES = frozenset({"sso", "scim", "roster", "lti", "ats", "manual"})
MATCH_QUEUE_STATUSES = frozenset({"pending", "linked", "created", "rejected"})


class ExternalIdentityLink(Base):
    __tablename__ = "intg_identity_links"
    __table_args__ = (
        # One ACTIVE link per (connection, subject); revoked links keep history.
        Index(
            "uq_intg_idlink_subject",
            "connection_ref",
            "subject",
            unique=True,
            postgresql_where="revoked_at IS NULL",
        ),
        Index("ix_intg_idlink_org_user", "org_id", "user_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    # sso_connection_id / integration connection id / scim token id — the
    # namespace the subject is stable within.
    connection_ref: Mapped[str] = mapped_column(String(26), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_at_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IdentityMatchQueue(Base):
    """Ambiguous external identities awaiting explicit admin confirmation."""

    __tablename__ = "intg_identity_match_queue"
    __table_args__ = (Index("ix_intg_idqueue_org_status", "org_id", "status"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    connection_ref: Mapped[str] = mapped_column(String(26), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    resolved_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
