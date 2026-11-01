"""Federation Collaboration, Reputation & Conformance (Issue #45 Parts K, N, P).

Cross-instance collaboration spaces, peer reputation scoring,
abuse reporting, and protocol conformance testing.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.federation import (
    FederationCircuitBreaker,
    FederationInstance,
    PeerIncident,
    PeerReputationScore,
)


class CollaborationNotFoundError(AppError):
    def __init__(self):
        super().__init__("COLLABORATION_NOT_FOUND", "Collaboration space not found", 404)


# ── Part K: Cross-instance Collaboration ─────────────────────────────
# Collaboration spaces use FederationGrant model for shared access


async def list_collaboration_grants(
    db: AsyncSession,
    org_id: str,
    *,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list, int]:
    from app.models.federation import FederationGrant

    base = select(FederationGrant).where(FederationGrant.org_id == org_id)
    count_q = select(func.count()).select_from(FederationGrant).where(FederationGrant.org_id == org_id)
    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederationGrant.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


GRANTABLE_TYPES = {"skill_pack", "workflow_pack", "project", "cohort"}
VALID_GRANT_PERMISSIONS = {"read", "comment", "fork", "install"}


async def create_collaboration_grant(
    db: AsyncSession,
    org_id: str,
    *,
    peer_instance_id: str,
    resource_type: str,
    resource_id: str,
    permissions: list,
    expires_at: str | None = None,
) -> object:
    from app.models.federation import FederationGrant

    # Validate resource type is grantable
    if resource_type not in GRANTABLE_TYPES:
        raise AppError(
            "INVALID_RESOURCE_TYPE",
            f"resource_type must be one of: {', '.join(sorted(GRANTABLE_TYPES))}",
            422,
        )

    # Validate permissions against allowlist
    invalid = set(permissions) - VALID_GRANT_PERMISSIONS
    if invalid:
        raise AppError(
            "INVALID_PERMISSIONS",
            f"Invalid permissions: {', '.join(sorted(invalid))}. Valid: {', '.join(sorted(VALID_GRANT_PERMISSIONS))}",
            422,
        )

    # Validate resource belongs to this org (IDOR guard)
    resource_models = {
        "skill_pack": ("app.models.skill_pack", "SkillPack", "owner_org_id"),
        "workflow_pack": ("app.models.workflow_pack", "WorkflowPack", "owner_org_id"),
        "project": ("app.models.project", "Project", "org_id"),
        "cohort": ("app.models.cohort", "Cohort", "org_id"),
    }
    mod_path, cls_name, org_col = resource_models[resource_type]
    import importlib
    mod = importlib.import_module(mod_path)
    model_cls = getattr(mod, cls_name)
    org_attr = getattr(model_cls, org_col)
    res = await db.execute(
        select(model_cls.id).where(model_cls.id == resource_id, org_attr == org_id)
    )
    if res.scalar_one_or_none() is None:
        raise AppError("RESOURCE_NOT_FOUND", f"{resource_type} not found in this org", 404)

    # Validate peer instance exists
    peer = await db.execute(
        select(FederationInstance).where(FederationInstance.id == peer_instance_id)
    )
    if peer.scalar_one_or_none() is None:
        raise AppError("PEER_NOT_FOUND", "Peer instance not found", 404)

    grant = FederationGrant(
        org_id=org_id,
        peer_instance_id=peer_instance_id,
        resource_type=resource_type,
        resource_id=resource_id,
        permissions=permissions,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        status="active",
    )
    db.add(grant)
    await db.flush()
    return grant


# ── Part N: Abuse / Reputation ───────────────────────────────────────


async def get_peer_reputation(
    db: AsyncSession,
    org_id: str,
    peer_instance_id: str,
) -> PeerReputationScore | None:
    result = await db.execute(
        select(PeerReputationScore).where(
            PeerReputationScore.org_id == org_id,
            PeerReputationScore.peer_instance_id == peer_instance_id,
        )
    )
    return result.scalar_one_or_none()


async def list_peer_reputations(
    db: AsyncSession,
    org_id: str,
) -> list[PeerReputationScore]:
    result = await db.execute(
        select(PeerReputationScore)
        .where(PeerReputationScore.org_id == org_id)
        .order_by(PeerReputationScore.score.desc())
    )
    return list(result.scalars().all())


async def report_peer_incident(
    db: AsyncSession,
    org_id: str,
    *,
    peer_instance_id: str,
    incident_type: str,
    title: str,
    description: str | None = None,
    severity: str = "medium",
    evidence: dict | None = None,
    reported_by: str | None = None,
) -> PeerIncident:
    incident = PeerIncident(
        org_id=org_id,
        peer_instance_id=peer_instance_id,
        incident_type=incident_type,
        title=title,
        description=description,
        severity=severity,
        evidence=evidence or {},
        reported_by=reported_by,
        status="reported",
    )
    db.add(incident)
    await db.flush()
    return incident


async def list_peer_incidents(
    db: AsyncSession,
    org_id: str,
    *,
    peer_instance_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[PeerIncident], int]:
    base = select(PeerIncident).where(PeerIncident.org_id == org_id)
    count_q = select(func.count()).select_from(PeerIncident).where(PeerIncident.org_id == org_id)

    if peer_instance_id:
        base = base.where(PeerIncident.peer_instance_id == peer_instance_id)
        count_q = count_q.where(PeerIncident.peer_instance_id == peer_instance_id)
    if status:
        base = base.where(PeerIncident.status == status)
        count_q = count_q.where(PeerIncident.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(PeerIncident.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Part P: Protocol Conformance ─────────────────────────────────────


async def check_protocol_conformance(
    db: AsyncSession,
    org_id: str,
    peer_instance_id: str,
) -> dict:
    """Check protocol conformance for a peer instance.

    Returns a conformance report with version compatibility,
    required capabilities, and circuit breaker status.
    """
    # Get peer info
    result = await db.execute(
        select(FederationInstance).where(
            FederationInstance.id == peer_instance_id,
        )
    )
    peer = result.scalar_one_or_none()
    if peer is None:
        raise AppError("PEER_NOT_FOUND", "Peer instance not found", 404)

    # Check circuit breaker
    cb_result = await db.execute(
        select(FederationCircuitBreaker).where(
            FederationCircuitBreaker.org_id == org_id,
            FederationCircuitBreaker.peer_instance_id == peer_instance_id,
        )
    )
    circuit_breaker = cb_result.scalar_one_or_none()

    return {
        "peer_id": peer_instance_id,
        "peer_uri": peer.instance_uri,
        "protocol_version": peer.protocol_version,
        "software_version": peer.software_version,
        "trust_status": peer.trust_status,
        "circuit_breaker": {
            "state": circuit_breaker.state if circuit_breaker else "closed",
            "failure_count": circuit_breaker.failure_count if circuit_breaker else 0,
            "last_failure_at": str(circuit_breaker.last_failure_at) if circuit_breaker and circuit_breaker.last_failure_at else None,
        } if True else None,
        "conformance": {
            "identity_verified": peer.trust_status in ("trusted", "verified"),
            "protocol_compatible": True,  # placeholder for version compat check
            "signing_key_valid": peer.signing_key_id is not None,
        },
    }


async def get_circuit_breaker(
    db: AsyncSession,
    org_id: str,
    peer_instance_id: str,
) -> FederationCircuitBreaker | None:
    result = await db.execute(
        select(FederationCircuitBreaker).where(
            FederationCircuitBreaker.org_id == org_id,
            FederationCircuitBreaker.peer_instance_id == peer_instance_id,
        )
    )
    return result.scalar_one_or_none()


async def list_circuit_breakers(
    db: AsyncSession,
    org_id: str,
) -> list[FederationCircuitBreaker]:
    result = await db.execute(
        select(FederationCircuitBreaker)
        .where(FederationCircuitBreaker.org_id == org_id)
        .order_by(FederationCircuitBreaker.created_at.desc())
    )
    return list(result.scalars().all())
