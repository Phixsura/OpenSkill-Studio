"""Client portal: members, guest links, approval records, shares
(ADR-014 §9)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class ClientPortalMember(Base):
    """A real user account bound to ONE commercial project as a client."""

    __tablename__ = "cp_client_portal_members"
    __table_args__ = (
        Index("uq_cp_portal_member", "project_id", "user_id", unique=True),
        Index("ix_cp_portal_members_user", "user_id"),
    )

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)  # reviewer | approver
    status: Mapped[str] = mapped_column(
        String(10), default="active", server_default="active"
    )  # active | revoked
    invited_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClientGuestLink(Base):
    """Secure, expiring, revocable guest access — raw token shown exactly
    once at creation; only the sha256 hash is stored."""

    __tablename__ = "cp_client_guest_links"
    __table_args__ = (Index("ix_cp_guest_links_project", "project_id"),)

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    label: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)  # optional binding
    role: Mapped[str] = mapped_column(String(10), nullable=False)  # reviewer | approver
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    use_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClientApprovalRecord(Base):
    """Append-only client decision history — kept STRICTLY separate from
    instructor SubmissionReview (issue §31)."""

    __tablename__ = "cp_client_approvals"
    __table_args__ = (
        Index("ix_cp_approvals_project", "project_id", "created_at"),
        Index("ix_cp_approvals_submission", "submission_id"),
        # Exactly one final acceptance per project — races become a clean 409
        Index(
            "uq_cp_final_accept",
            "project_id",
            unique=True,
            postgresql_where="action = 'final_accepted'",
        ),
    )

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    submission_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # revision_requested | approved | final_accepted
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    acted_by_user_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    acted_by_link_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    acted_by_label: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClientShare(Base):
    """Whitelist of submissions visible in the portal."""

    __tablename__ = "cp_client_shares"

    id: Mapped[str] = ulid_pk()
    project_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    submission_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("submissions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    shared_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
