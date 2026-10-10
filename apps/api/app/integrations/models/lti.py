"""LTI 1.3 tool-side models (ADR-018 §8).

A registration is one platform (LMS) issuer+client; deployments are the
platform's placements (launches with an unlisted deployment_id are
rejected). Resource links map LMS placements to platform objects; grade
return (AGS) is opt-in per link. Launch states are the single-use
state/nonce rows for the OIDC third-party-initiated flow.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk

LTI_RESOURCE_KINDS = frozenset({"skill", "project", "learning_path"})
LTI_MESSAGE_TYPES = frozenset({"LtiResourceLinkRequest", "LtiDeepLinkingRequest"})


class LtiRegistration(Base):
    __tablename__ = "intg_lti_registrations"
    __table_args__ = (
        Index("uq_intg_lti_reg", "issuer", "client_id", unique=True),
        Index("ix_intg_lti_reg_org", "org_id"),
    )

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    issuer: Mapped[str] = mapped_column(String(500), nullable=False)
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    auth_login_url: Mapped[str] = mapped_column(String(500), nullable=False)
    auth_token_url: Mapped[str] = mapped_column(String(500), nullable=False)
    jwks_url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    allow_jit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    default_role: Mapped[str] = mapped_column(String(30), nullable=False, default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LtiDeployment(Base):
    __tablename__ = "intg_lti_deployments"
    __table_args__ = (
        Index("uq_intg_lti_deploy", "registration_id", "deployment_id", unique=True),
    )

    id: Mapped[str] = ulid_pk()
    registration_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_lti_registrations.id", ondelete="CASCADE"), nullable=False
    )
    deployment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LtiResourceLink(Base):
    __tablename__ = "intg_lti_resource_links"
    __table_args__ = (
        Index(
            "uq_intg_lti_rlink",
            "registration_id",
            "deployment_id",
            "resource_link_id",
            unique=True,
        ),
    )

    id: Mapped[str] = ulid_pk()
    registration_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_lti_registrations.id", ondelete="CASCADE"), nullable=False
    )
    deployment_id: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_link_id: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    target_id: Mapped[str] = mapped_column(String(26), nullable=False)
    # AGS: grade return is explicit + configurable per link (issue Part J).
    ags_lineitem_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    grade_sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LtiLaunchState(Base):
    """Single-use state/nonce for the OIDC third-party-initiated flow."""

    __tablename__ = "intg_lti_launch_states"
    __table_args__ = (Index("ix_intg_lti_state_expiry", "expires_at"),)

    id: Mapped[str] = ulid_pk()  # the `state` value
    registration_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("intg_lti_registrations.id", ondelete="CASCADE"), nullable=False
    )
    nonce: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LtiToolKey(Base):
    """The tool's signing keypair (AGS client assertions, deep-link JWTs).
    Private key is a crypto.py envelope; the public JWK serves at /lti/jwks."""

    __tablename__ = "intg_lti_tool_keys"

    id: Mapped[str] = ulid_pk()
    kid: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    private_pem_ct: Mapped[str] = mapped_column(Text, nullable=False)
    public_jwk: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default="{}")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
