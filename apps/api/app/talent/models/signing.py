"""Org signing key management for W3C VC / Open Badges 3.0 (ADR-015 D-VC).

Each organization has one or more Ed25519 keypairs used to sign
credentials and passport snapshots. Keys can be rotated; old keys
remain for verification but are marked 'rotated'.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ulid_pk


class OrgSigningKey(Base):
    """Ed25519 signing keypair belonging to an organization."""

    __tablename__ = "talent_org_signing_keys"


    def __repr__(self) -> str:
        return f"<OrgSigningKey {self.id}>"

    id: Mapped[str] = ulid_pk()
    org_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("organizations.id", ondelete="CASCADE")
    )
    key_type: Mapped[str] = mapped_column(String(20), default="ed25519", server_default="'ed25519'")
    # PEM-encoded public key (safe to expose)
    public_key: Mapped[str] = mapped_column(String(500))
    # PEM-encoded private key (encrypted at rest via app secret)
    private_key_encrypted: Mapped[str] = mapped_column(String(500))
    # active | rotated | revoked
    status: Mapped[str] = mapped_column(String(20), default="active", server_default="'active'")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_talent_org_signing_keys_org", "org_id", "status"),)
