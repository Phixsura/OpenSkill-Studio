"""SCIM 2.0 provisioning models (ADR-018 §5.3).

Tokens are per-org bearers: the URL carries no org id (IdPs can't template
paths), so the token IS the tenant resolution. Groups mirror the IdP's
groups; membership effects (cohort / org-role mapping) are driven by the
token's group_map and applied through the same service functions the UI uses.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

MAX_SCIM_TOKENS_PER_ORG = 5
SCIM_TOKEN_PREFIX = "osks_scim_"

# group_map entry kinds: {"IdP Group Name": {"kind":"cohort","id":...} |
# {"kind":"role","role":"instructor"}}. Role mapping honors the same mint
# ceiling as JIT (student|instructor) — owner/admin stay human-granted.
GROUP_MAP_KINDS = frozenset({"cohort", "role"})


class ScimToken(Base):
    __tablename__ = "intg_scim_tokens"
    __table_args__ = (Index("ix_intg_scim_tokens_org", "org_id", "revoked_at"),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    group_map: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ScimGroup(Base):
    __tablename__ = "intg_scim_groups"
    __table_args__ = (Index("uq_intg_scim_group_org_name", "org_id", "display_name", unique=True),)

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ScimGroupMember(Base):
    __tablename__ = "intg_scim_group_members"
    __table_args__ = (Index("uq_intg_scim_gm", "group_id", "user_id", unique=True),)

    id: Mapped[str] = ulid_pk()
    group_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_scim_groups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
