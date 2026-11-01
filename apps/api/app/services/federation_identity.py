"""Federation instance identity — manage local identity, peering handshake, key rotation (ADR-017 Part A)."""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import AppError
from app.models.federation import (
    FederationInstance,
    InstanceTrustStatus,
    LocalInstanceIdentity,
    PeerReputationScore,
)
from app.services.federation_crypto import generate_ed25519_keypair

log = structlog.get_logger()

KEY_ROTATION_GRACE_DAYS = 30


class FederationIdentityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Local identity ───────────────────────────────────

    async def get_or_create_identity(self) -> LocalInstanceIdentity:
        """Return the singleton local identity, creating it if needed."""
        identity = await self.db.get(LocalInstanceIdentity, "self")
        if identity is not None:
            return identity

        private_pem, public_pem, key_id = generate_ed25519_keypair()

        identity = LocalInstanceIdentity(
            id="self",
            instance_uri=self._default_instance_uri(),
            display_name="OpenSkill Instance",
            signing_key_pem=private_pem,
            public_key_pem=public_pem,
            key_id=key_id,
            key_generated_at=datetime.now(UTC),
            protocol_version="1.0",
            extra_metadata={},
        )
        self.db.add(identity)
        await self.db.flush()
        log.info("federation.identity_created", key_id=key_id)
        return identity

    async def update_identity(
        self,
        display_name: str | None = None,
        metadata: dict | None = None,
    ) -> LocalInstanceIdentity:
        identity = await self.get_or_create_identity()
        if display_name is not None:
            identity.display_name = display_name
        if metadata is not None:
            identity.extra_metadata = metadata
        await self.db.flush()
        return identity

    async def rotate_key(self) -> LocalInstanceIdentity:
        """Generate a new keypair; move current to previous with grace period."""
        identity = await self.get_or_create_identity()

        # Move current → previous
        identity.previous_signing_key_pem = identity.signing_key_pem
        identity.previous_key_id = identity.key_id
        identity.previous_key_expires_at = datetime.now(UTC) + timedelta(
            days=KEY_ROTATION_GRACE_DAYS
        )

        # Generate new
        private_pem, public_pem, key_id = generate_ed25519_keypair()
        identity.signing_key_pem = private_pem
        identity.public_key_pem = public_pem
        identity.key_id = key_id
        identity.key_generated_at = datetime.now(UTC)

        await self.db.flush()
        log.info(
            "federation.key_rotated",
            new_key_id=key_id,
            previous_key_id=identity.previous_key_id,
            grace_expires=identity.previous_key_expires_at,
        )
        return identity

    async def get_well_known(self) -> dict:
        """Build the /.well-known/openskill-federation response."""
        identity = await self.get_or_create_identity()
        return {
            "instance_uri": identity.instance_uri,
            "display_name": identity.display_name,
            "public_key_pem": identity.public_key_pem,
            "key_id": identity.key_id,
            "protocol_version": identity.protocol_version,
            "software_version": getattr(settings, "app_version", "0.1.0"),
            "metadata": identity.extra_metadata,
            "supported_artifact_types": [
                "skill_pack", "workflow_pack", "credential", "opportunity",
                "marketplace_listing", "ecosystem_observation",
            ],
            "federation_endpoints": {
                "registry_sync": "/api/v1/federation/registry/sync",
                "credential_verify": "/api/v1/federation/credentials/verify",
                "opportunity_search": "/api/v1/federation/opportunities/search",
                "revocation_status": "/api/v1/federation/revocations/status",
            },
        }

    # ── Peer management ──────────────────────────────────

    async def add_peer(self, instance_uri: str) -> FederationInstance:
        """Register a new federation peer by its instance_uri.

        Does NOT automatically trust — admin must set trust_status separately.
        """
        identity = await self.get_or_create_identity()
        if instance_uri.rstrip("/") == identity.instance_uri.rstrip("/"):
            raise AppError("SELF_PEERING_FORBIDDEN", "Cannot add self as federation peer", 422)

        # Check duplicate
        existing = await self.db.execute(
            select(FederationInstance).where(FederationInstance.instance_uri == instance_uri)
        )
        if existing.scalar_one_or_none() is not None:
            raise AppError("PEER_ALREADY_EXISTS", f"Peer {instance_uri} already registered", 409)

        # In production, we'd fetch /.well-known/openskill-federation from the peer.
        # For now, create a placeholder that admin will populate.
        peer = FederationInstance(
            instance_uri=instance_uri,
            display_name=instance_uri,  # placeholder
            protocol_version="1.0",
            public_key_pem="",  # must be populated via handshake or manual entry
            key_id="",
            trust_status=InstanceTrustStatus.PENDING,
            extra_metadata={},
        )
        self.db.add(peer)
        await self.db.flush()

        # Initialize reputation score
        rep = PeerReputationScore(instance_id=peer.id)
        self.db.add(rep)
        await self.db.flush()

        log.info("federation.peer_added", peer_id=peer.id, instance_uri=instance_uri)
        return peer

    async def get_peer(self, peer_id: str) -> FederationInstance:
        peer = await self.db.get(FederationInstance, peer_id)
        if peer is None:
            raise AppError("PEER_NOT_FOUND", "Peer instance not found", 404)
        return peer

    async def list_peers(
        self,
        trust_status: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[FederationInstance], int]:
        stmt = select(FederationInstance)
        count_stmt = select(FederationInstance)

        if trust_status:
            stmt = stmt.where(
                FederationInstance.trust_status == InstanceTrustStatus(trust_status)
            )
            count_stmt = count_stmt.where(
                FederationInstance.trust_status == InstanceTrustStatus(trust_status)
            )

        from sqlalchemy import func as sqla_func

        total_result = await self.db.execute(
            count_stmt.with_only_columns(sqla_func.count(FederationInstance.id))
        )
        total = total_result.scalar() or 0

        stmt = stmt.order_by(FederationInstance.created_at.desc())
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(stmt)
        peers = list(result.scalars().all())

        return peers, total

    async def update_peer(
        self,
        peer_id: str,
        trust_status: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
    ) -> FederationInstance:
        peer = await self.get_peer(peer_id)
        if trust_status is not None:
            peer.trust_status = InstanceTrustStatus(trust_status)
        if display_name is not None:
            peer.display_name = display_name
        if description is not None:
            peer.description = description
        await self.db.flush()
        log.info("federation.peer_updated", peer_id=peer_id, trust_status=trust_status)
        return peer

    async def remove_peer(self, peer_id: str) -> None:
        peer = await self.get_peer(peer_id)
        await self.db.delete(peer)
        await self.db.flush()
        log.info("federation.peer_removed", peer_id=peer_id)

    async def get_peer_reputation(self, peer_id: str) -> PeerReputationScore | None:
        return await self.db.get(PeerReputationScore, peer_id)

    # ── Helpers ──────────────────────────────────────────

    @staticmethod
    def _default_instance_uri() -> str:
        base = getattr(settings, "base_url", None) or "https://localhost:8000"
        return base.rstrip("/")
