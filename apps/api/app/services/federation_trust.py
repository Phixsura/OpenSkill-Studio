"""Federation trust registry — policy evaluation, envelope verification, reputation (ADR-017 Parts C, L, N)."""

from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.federation import (
    FederationInstance,
    FederationRevocation,
    IncidentSeverity,
    IncidentType,
    InstanceTrustStatus,
    PeerIncident,
    PeerReputationScore,
    RevocationType,
    TrustAction,
    TrustArtifactType,
    TrustPolicy,
)
from app.services.federation_crypto import verify_envelope_with_peer

log = structlog.get_logger()

# ── Auto-suspension thresholds ───────────────────────────

INVALID_SIGNATURE_RATE_THRESHOLD = 0.05
SPAM_SCORE_THRESHOLD = 0.8
POLICY_VIOLATIONS_PER_DAY_THRESHOLD = 10


class FederationTrustService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Trust policy CRUD ────────────────────────────────

    async def create_policy(
        self,
        instance_id: str,
        artifact_type: str,
        action: str,
        conditions: dict | None = None,
        priority: int = 0,
        created_by: str | None = None,
    ) -> TrustPolicy:
        policy = TrustPolicy(
            instance_id=instance_id,
            artifact_type=TrustArtifactType(artifact_type),
            action=TrustAction(action),
            conditions=conditions,
            priority=priority,
            enabled=True,
            created_by=created_by,
        )
        self.db.add(policy)
        await self.db.flush()
        log.info(
            "federation.trust_policy_created",
            policy_id=policy.id,
            instance_id=instance_id,
            artifact_type=artifact_type,
            action=action,
        )
        return policy

    async def update_policy(
        self,
        policy_id: str,
        action: str | None = None,
        conditions: dict | None = None,
        priority: int | None = None,
        enabled: bool | None = None,
    ) -> TrustPolicy:
        policy = await self.db.get(TrustPolicy, policy_id)
        if policy is None:
            raise AppError("TRUST_POLICY_NOT_FOUND", "Trust policy not found", 404)
        if action is not None:
            policy.action = TrustAction(action)
        if conditions is not None:
            policy.conditions = conditions
        if priority is not None:
            policy.priority = priority
        if enabled is not None:
            policy.enabled = enabled
        await self.db.flush()
        return policy

    async def delete_policy(self, policy_id: str) -> None:
        policy = await self.db.get(TrustPolicy, policy_id)
        if policy is None:
            raise AppError("TRUST_POLICY_NOT_FOUND", "Trust policy not found", 404)
        await self.db.delete(policy)
        await self.db.flush()

    async def list_policies(
        self, instance_id: str, enabled_only: bool = False
    ) -> list[TrustPolicy]:
        stmt = (
            select(TrustPolicy)
            .where(TrustPolicy.instance_id == instance_id)
            .order_by(TrustPolicy.priority)
        )
        if enabled_only:
            stmt = stmt.where(TrustPolicy.enabled.is_(True))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ── Policy evaluation ────────────────────────────────

    async def evaluate_trust(
        self, peer_id: str, artifact_type: str, artifact: dict | None = None
    ) -> str:
        """Evaluate trust policy for a peer + artifact type.

        Returns 'accept', 'mirror', or 'reject'.
        Default deny: federation is opt-in.
        """
        # First check peer trust status
        peer = await self.db.get(FederationInstance, peer_id)
        if peer is None or peer.trust_status != InstanceTrustStatus.TRUSTED:
            return "reject"

        # Try type-specific policies first
        policies = await self.list_policies(peer_id, enabled_only=True)

        # Filter to matching type
        type_policies = [
            p for p in policies
            if p.artifact_type.value == artifact_type
        ]

        # Fall back to "all" policies
        if not type_policies:
            type_policies = [
                p for p in policies
                if p.artifact_type == TrustArtifactType.ALL
            ]

        for policy in type_policies:
            if self._matches_conditions(policy.conditions, artifact):
                return policy.action.value

        # Default deny
        return "reject"

    @staticmethod
    def _matches_conditions(conditions: dict | None, artifact: dict | None) -> bool:
        """Check if an artifact matches policy conditions."""
        if not conditions:
            return True  # No conditions = match all
        if not artifact:
            return True  # No artifact to check against = match

        # Category filter
        allowed_categories = conditions.get("categories")
        if allowed_categories and artifact.get("category") not in allowed_categories:
            return False

        # Minimum version filter (simple string comparison; works for semver)
        min_version = conditions.get("min_version")
        if min_version and artifact.get("version") and artifact["version"] < min_version:
            return False

        # Tag filter
        required_tags = conditions.get("required_tags")
        if required_tags:
            artifact_tags = set(artifact.get("tags", []))
            if not set(required_tags).issubset(artifact_tags):
                return False

        return True

    # ── Envelope verification with trust ─────────────────

    async def verify_and_accept_envelope(
        self, envelope: dict
    ) -> tuple[bool, FederationInstance | None, str]:
        """Verify envelope signature and check trust policy.

        Returns (accepted, peer, reason).
        """
        source_instance_uri = envelope.get("source_instance")
        if not source_instance_uri:
            return False, None, "Missing source_instance"

        # Find peer
        result = await self.db.execute(
            select(FederationInstance).where(
                FederationInstance.instance_uri == source_instance_uri
            )
        )
        peer = result.scalar_one_or_none()
        if peer is None:
            return False, None, "Unknown source instance"

        if peer.trust_status != InstanceTrustStatus.TRUSTED:
            return False, peer, f"Peer not trusted (status={peer.trust_status.value})"

        # Check reputation auto-suspension
        rep = await self.db.get(PeerReputationScore, peer.id)
        if rep and rep.auto_suspended:
            return False, peer, "Peer auto-suspended due to reputation"

        # Verify signature
        sig_valid = verify_envelope_with_peer(
            envelope=envelope,
            peer_key_id=peer.key_id,
            peer_public_key_pem=peer.public_key_pem,
            peer_previous_key_id=peer.previous_key_id,
            peer_previous_key_pem=peer.previous_key_pem,
            peer_previous_key_expires_at=peer.previous_key_expires_at,
        )

        if not sig_valid:
            await self._record_incident(
                peer.id,
                IncidentType.INVALID_SIGNATURE,
                IncidentSeverity.MEDIUM,
                f"Invalid signature on envelope {envelope.get('envelope_id')}",
                envelope.get("envelope_id"),
            )
            return False, peer, "Invalid envelope signature"

        # Check expiry
        expires_at = envelope.get("expires_at")
        if expires_at:
            from dateutil.parser import isoparse

            if isoparse(expires_at) < datetime.now(UTC):
                return False, peer, "Envelope expired"

        # Update reputation counter
        if rep:
            rep.total_envelopes_received = (rep.total_envelopes_received or 0) + 1
            await self.db.flush()

        # Update last_seen
        peer.last_seen_at = datetime.now(UTC)
        await self.db.flush()

        # Evaluate trust policy for the artifact type
        envelope_type = envelope.get("envelope_type", "")
        trust_action = await self.evaluate_trust(peer.id, envelope_type, envelope.get("payload"))
        if trust_action == "reject":
            return False, peer, f"Trust policy rejects {envelope_type}"

        return True, peer, trust_action

    # ── Revocations ──────────────────────────────────────

    async def process_revocation(
        self, envelope: dict, peer: FederationInstance
    ) -> FederationRevocation:
        """Process a signed revocation envelope."""
        payload = envelope.get("payload", {})
        revocation = FederationRevocation(
            instance_id=peer.id,
            revocation_type=RevocationType(payload["revocation_type"]),
            target_type=payload["target_type"],
            target_id=payload["target_id"],
            reason=payload.get("reason"),
            revoked_at=datetime.now(UTC),
            envelope_id=envelope["envelope_id"],
            processed=False,
        )
        self.db.add(revocation)

        # Update reputation
        rep = await self.db.get(PeerReputationScore, peer.id)
        if rep:
            rep.revocations_issued = (rep.revocations_issued or 0) + 1

        await self.db.flush()
        log.info(
            "federation.revocation_received",
            revocation_id=revocation.id,
            target_type=payload["target_type"],
            target_id=payload["target_id"],
        )
        return revocation

    async def list_revocations(
        self, processed: bool | None = None, page: int = 1, per_page: int = 20
    ) -> tuple[list[FederationRevocation], int]:
        stmt = select(FederationRevocation)
        if processed is not None:
            stmt = stmt.where(FederationRevocation.processed == processed)

        from sqlalchemy import func as sqla_func

        count_result = await self.db.execute(
            stmt.with_only_columns(sqla_func.count(FederationRevocation.id))
        )
        total = count_result.scalar() or 0

        stmt = select(FederationRevocation).order_by(FederationRevocation.created_at.desc())
        if processed is not None:
            stmt = stmt.where(FederationRevocation.processed == processed)
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    # ── Incidents & reputation ───────────────────────────

    async def _record_incident(
        self,
        instance_id: str,
        incident_type: IncidentType,
        severity: IncidentSeverity,
        description: str,
        envelope_id: str | None = None,
    ) -> PeerIncident:
        incident = PeerIncident(
            instance_id=instance_id,
            incident_type=incident_type,
            severity=severity,
            description=description,
            envelope_id=envelope_id,
        )
        self.db.add(incident)

        # Update reputation counters
        rep = await self.db.get(PeerReputationScore, instance_id)
        if rep:
            if incident_type == IncidentType.INVALID_SIGNATURE:
                rep.invalid_signatures = (rep.invalid_signatures or 0) + 1
            elif incident_type == IncidentType.POLICY_VIOLATION:
                rep.policy_violations = (rep.policy_violations or 0) + 1
            rep.last_incident_at = datetime.now(UTC)

            # Check auto-suspension
            await self._check_auto_suspension(rep)

        await self.db.flush()
        log.warning(
            "federation.incident_recorded",
            instance_id=instance_id,
            incident_type=incident_type.value,
            severity=severity.value,
        )
        return incident

    async def _check_auto_suspension(self, rep: PeerReputationScore) -> None:
        """Auto-suspend peer if thresholds are exceeded."""
        if rep.auto_suspended:
            return

        should_suspend = False
        reason = ""

        # Invalid signature rate
        if rep.total_envelopes_received and rep.total_envelopes_received > 100:
            rate = rep.invalid_signatures / rep.total_envelopes_received
            if rate > INVALID_SIGNATURE_RATE_THRESHOLD:
                should_suspend = True
                reason = f"Invalid signature rate {rate:.2%} exceeds {INVALID_SIGNATURE_RATE_THRESHOLD:.0%}"

        # Spam score
        if rep.spam_score > SPAM_SCORE_THRESHOLD:
            should_suspend = True
            reason = f"Spam score {rep.spam_score:.2f} exceeds {SPAM_SCORE_THRESHOLD}"

        if should_suspend:
            rep.auto_suspended = True
            # Also update the peer's trust status
            peer = await self.db.get(FederationInstance, rep.instance_id)
            if peer:
                peer.trust_status = InstanceTrustStatus.SUSPENDED
            log.warning(
                "federation.peer_auto_suspended",
                instance_id=rep.instance_id,
                reason=reason,
            )

    async def list_incidents(
        self,
        instance_id: str | None = None,
        unresolved_only: bool = False,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PeerIncident], int]:
        stmt = select(PeerIncident)
        if instance_id:
            stmt = stmt.where(PeerIncident.instance_id == instance_id)
        if unresolved_only:
            stmt = stmt.where(PeerIncident.resolved_at.is_(None))

        from sqlalchemy import func as sqla_func

        count_result = await self.db.execute(
            stmt.with_only_columns(sqla_func.count(PeerIncident.id))
        )
        total = count_result.scalar() or 0

        stmt = select(PeerIncident).order_by(PeerIncident.created_at.desc())
        if instance_id:
            stmt = stmt.where(PeerIncident.instance_id == instance_id)
        if unresolved_only:
            stmt = stmt.where(PeerIncident.resolved_at.is_(None))
        stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def resolve_incident(self, incident_id: str, resolved_by: str) -> PeerIncident:
        incident = await self.db.get(PeerIncident, incident_id)
        if incident is None:
            raise AppError("INCIDENT_NOT_FOUND", "Incident not found", 404)
        incident.resolved_at = datetime.now(UTC)
        incident.resolved_by = resolved_by
        await self.db.flush()
        return incident
