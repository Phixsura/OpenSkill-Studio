import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, ulid_pk


class OrgStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class OrgRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    STUDENT = "student"


# Role hierarchy — lower index = higher privilege
ROLE_HIERARCHY = {
    OrgRole.OWNER: 0,
    OrgRole.ADMIN: 1,
    OrgRole.INSTRUCTOR: 2,
    OrgRole.STUDENT: 3,
}


class MemberStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = ulid_pk()
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[OrgStatus] = mapped_column(
        Enum(OrgStatus, name="org_status", create_constraint=True),
        default=OrgStatus.ACTIVE,
    )
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    members: Mapped[list["OrgMember"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    invitations: Mapped[list["OrgInvitation"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )
    invite_links: Mapped[list["OrgInviteLink"]] = relationship(
        back_populates="organization", cascade="all, delete-orphan"
    )


class OrgMember(Base):
    __tablename__ = "org_members"
    __table_args__ = (
        Index("uq_org_member", "org_id", "user_id", unique=True),
        Index("ix_org_members_user", "user_id"),
        Index("ix_org_members_org_role", "org_id", "role"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[OrgRole] = mapped_column(
        Enum(OrgRole, name="org_role", create_constraint=True),
        default=OrgRole.STUDENT,
    )
    status: Mapped[MemberStatus] = mapped_column(
        Enum(MemberStatus, name="member_status", create_constraint=True),
        default=MemberStatus.ACTIVE,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    invited_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])  # noqa: F821


class OrgInvitation(Base):
    __tablename__ = "org_invitations"
    __table_args__ = (
        Index("ix_org_invitations_org_status", "org_id", "status"),
        Index("ix_org_invitations_email_status", "email", "status"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[OrgRole] = mapped_column(
        Enum(OrgRole, name="org_role", create_constraint=True),
        default=OrgRole.STUDENT,
    )
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    invited_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    status: Mapped[InviteStatus] = mapped_column(
        Enum(InviteStatus, name="invite_status", create_constraint=True),
        default=InviteStatus.PENDING,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="invitations")


class OrgInviteLink(Base):
    __tablename__ = "org_invite_links"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    role: Mapped[OrgRole] = mapped_column(
        Enum(OrgRole, name="org_role", create_constraint=True),
        default=OrgRole.STUDENT,
    )
    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="invite_links")
