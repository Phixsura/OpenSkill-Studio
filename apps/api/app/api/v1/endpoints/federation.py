"""Federation API endpoints — peer management, trust policies, identity, well-known (ADR-017)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole
from app.schemas.base import DataResponse, ListResponse, PaginationMeta
from app.schemas.federation import (
    AddPeerRequest,
    CreateTrustPolicyRequest,
    InstanceIdentityResponse,
    PeerIncidentResponse,
    PeerReputationSummary,
    PeerResponse,
    ResolveIncidentRequest,
    RevocationResponse,
    TrustPolicyResponse,
    UpdateInstanceIdentityRequest,
    UpdatePeerRequest,
    UpdateTrustPolicyRequest,
    WellKnownFederationResponse,
)
from app.services.federation_identity import FederationIdentityService
from app.services.federation_trust import FederationTrustService

router = APIRouter()

# ── Well-known (public, no auth) ─────────────────────────


@router.get(
    "/.well-known/openskill-federation",
    response_model=WellKnownFederationResponse,
    tags=["federation"],
)
async def well_known_federation(
    db: AsyncSession = Depends(get_db),
):
    """Public endpoint for federation discovery."""
    svc = FederationIdentityService(db)
    data = await svc.get_well_known()
    return data


# ── Instance Identity (admin) ────────────────────────────


@router.get(
    "/federation/identity",
    response_model=DataResponse[InstanceIdentityResponse],
    tags=["federation"],
)
async def get_identity(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    identity = await svc.get_or_create_identity()
    return {
        "data": {
            "instance_uri": identity.instance_uri,
            "display_name": identity.display_name,
            "public_key_pem": identity.public_key_pem,
            "key_id": identity.key_id,
            "protocol_version": identity.protocol_version,
            "metadata": identity.extra_metadata,
        }
    }


@router.put(
    "/federation/identity",
    response_model=DataResponse[InstanceIdentityResponse],
    tags=["federation"],
)
async def update_identity(
    body: UpdateInstanceIdentityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    identity = await svc.update_identity(
        display_name=body.display_name,
        metadata=body.metadata,
    )
    return {
        "data": {
            "instance_uri": identity.instance_uri,
            "display_name": identity.display_name,
            "public_key_pem": identity.public_key_pem,
            "key_id": identity.key_id,
            "protocol_version": identity.protocol_version,
            "metadata": identity.extra_metadata,
        }
    }


@router.post(
    "/federation/identity/rotate-key",
    response_model=DataResponse[InstanceIdentityResponse],
    tags=["federation"],
)
async def rotate_key(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    identity = await svc.rotate_key()
    return {
        "data": {
            "instance_uri": identity.instance_uri,
            "display_name": identity.display_name,
            "public_key_pem": identity.public_key_pem,
            "key_id": identity.key_id,
            "protocol_version": identity.protocol_version,
            "metadata": identity.extra_metadata,
        }
    }


# ── Peer Management (admin) ─────────────────────────────


@router.get(
    "/federation/peers",
    response_model=ListResponse[PeerResponse],
    tags=["federation"],
)
async def list_peers(
    trust_status: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    peers, total = await svc.list_peers(trust_status=trust_status, page=page, per_page=per_page)

    data = []
    for peer in peers:
        rep = await svc.get_peer_reputation(peer.id)
        rep_summary = None
        if rep:
            total_env = rep.total_envelopes_received or 0
            rate = (rep.invalid_signatures / total_env) if total_env > 0 else 0.0
            rep_summary = PeerReputationSummary(
                total_envelopes=total_env,
                invalid_signature_rate=round(rate, 4),
                spam_score=round(rep.spam_score, 4),
            )
        data.append(
            PeerResponse(
                id=peer.id,
                instance_uri=peer.instance_uri,
                display_name=peer.display_name,
                description=peer.description,
                logo_url=peer.logo_url,
                software_version=peer.software_version,
                protocol_version=peer.protocol_version,
                key_id=peer.key_id,
                trust_status=peer.trust_status.value,
                last_seen_at=peer.last_seen_at,
                last_sync_error=peer.last_sync_error,
                reputation=rep_summary,
                created_at=peer.created_at,
                updated_at=peer.updated_at,
            )
        )

    return {
        "data": data,
        "meta": PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page < total)
        ),
    }


@router.post(
    "/federation/peers",
    response_model=DataResponse[PeerResponse],
    status_code=201,
    tags=["federation"],
)
async def add_peer(
    body: AddPeerRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    peer = await svc.add_peer(body.instance_uri)
    return {
        "data": PeerResponse(
            id=peer.id,
            instance_uri=peer.instance_uri,
            display_name=peer.display_name,
            protocol_version=peer.protocol_version,
            key_id=peer.key_id,
            trust_status=peer.trust_status.value,
            created_at=peer.created_at,
            updated_at=peer.updated_at,
        )
    }


@router.get(
    "/federation/peers/{peer_id}",
    response_model=DataResponse[PeerResponse],
    tags=["federation"],
)
async def get_peer(
    peer_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    peer = await svc.get_peer(peer_id)
    rep = await svc.get_peer_reputation(peer.id)
    rep_summary = None
    if rep:
        total_env = rep.total_envelopes_received or 0
        rate = (rep.invalid_signatures / total_env) if total_env > 0 else 0.0
        rep_summary = PeerReputationSummary(
            total_envelopes=total_env,
            invalid_signature_rate=round(rate, 4),
            spam_score=round(rep.spam_score, 4),
        )
    return {
        "data": PeerResponse(
            id=peer.id,
            instance_uri=peer.instance_uri,
            display_name=peer.display_name,
            description=peer.description,
            logo_url=peer.logo_url,
            software_version=peer.software_version,
            protocol_version=peer.protocol_version,
            key_id=peer.key_id,
            trust_status=peer.trust_status.value,
            last_seen_at=peer.last_seen_at,
            last_sync_error=peer.last_sync_error,
            reputation=rep_summary,
            created_at=peer.created_at,
            updated_at=peer.updated_at,
        )
    }


@router.patch(
    "/federation/peers/{peer_id}",
    response_model=DataResponse[PeerResponse],
    tags=["federation"],
)
async def update_peer(
    peer_id: str,
    body: UpdatePeerRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    peer = await svc.update_peer(
        peer_id,
        trust_status=body.trust_status,
        display_name=body.display_name,
        description=body.description,
    )
    return {
        "data": PeerResponse(
            id=peer.id,
            instance_uri=peer.instance_uri,
            display_name=peer.display_name,
            description=peer.description,
            logo_url=peer.logo_url,
            software_version=peer.software_version,
            protocol_version=peer.protocol_version,
            key_id=peer.key_id,
            trust_status=peer.trust_status.value,
            last_seen_at=peer.last_seen_at,
            last_sync_error=peer.last_sync_error,
            created_at=peer.created_at,
            updated_at=peer.updated_at,
        )
    }


@router.delete(
    "/federation/peers/{peer_id}",
    status_code=204,
    tags=["federation"],
)
async def remove_peer(
    peer_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    svc = FederationIdentityService(db)
    await svc.remove_peer(peer_id)


# ── Trust Policies (admin) ──────────────────────────────


@router.get(
    "/federation/peers/{peer_id}/trust-policies",
    response_model=DataResponse[list[TrustPolicyResponse]],
    tags=["federation"],
)
async def list_trust_policies(
    peer_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    # Verify peer exists
    id_svc = FederationIdentityService(db)
    await id_svc.get_peer(peer_id)

    trust_svc = FederationTrustService(db)
    policies = await trust_svc.list_policies(peer_id)
    return {
        "data": [
            TrustPolicyResponse(
                id=p.id,
                instance_id=p.instance_id,
                artifact_type=p.artifact_type.value,
                action=p.action.value,
                conditions=p.conditions,
                priority=p.priority,
                enabled=p.enabled,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in policies
        ]
    }


@router.post(
    "/federation/peers/{peer_id}/trust-policies",
    response_model=DataResponse[TrustPolicyResponse],
    status_code=201,
    tags=["federation"],
)
async def create_trust_policy(
    peer_id: str,
    body: CreateTrustPolicyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    # Verify peer exists
    id_svc = FederationIdentityService(db)
    await id_svc.get_peer(peer_id)

    trust_svc = FederationTrustService(db)
    policy = await trust_svc.create_policy(
        instance_id=peer_id,
        artifact_type=body.artifact_type,
        action=body.action,
        conditions=body.conditions,
        priority=body.priority,
        created_by=user.id,
    )
    return {
        "data": TrustPolicyResponse(
            id=policy.id,
            instance_id=policy.instance_id,
            artifact_type=policy.artifact_type.value,
            action=policy.action.value,
            conditions=policy.conditions,
            priority=policy.priority,
            enabled=policy.enabled,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )
    }


@router.patch(
    "/federation/peers/{peer_id}/trust-policies/{policy_id}",
    response_model=DataResponse[TrustPolicyResponse],
    tags=["federation"],
)
async def update_trust_policy(
    peer_id: str,
    policy_id: str,
    body: UpdateTrustPolicyRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    trust_svc = FederationTrustService(db)
    policy = await trust_svc.update_policy(
        policy_id=policy_id,
        action=body.action,
        conditions=body.conditions,
        priority=body.priority,
        enabled=body.enabled,
    )
    return {
        "data": TrustPolicyResponse(
            id=policy.id,
            instance_id=policy.instance_id,
            artifact_type=policy.artifact_type.value,
            action=policy.action.value,
            conditions=policy.conditions,
            priority=policy.priority,
            enabled=policy.enabled,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
        )
    }


@router.delete(
    "/federation/peers/{peer_id}/trust-policies/{policy_id}",
    status_code=204,
    tags=["federation"],
)
async def delete_trust_policy(
    peer_id: str,
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    trust_svc = FederationTrustService(db)
    await trust_svc.delete_policy(policy_id)


# ── Revocations (admin) ─────────────────────────────────


@router.get(
    "/federation/revocations",
    response_model=ListResponse[RevocationResponse],
    tags=["federation"],
)
async def list_revocations(
    processed: bool | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    trust_svc = FederationTrustService(db)
    revocations, total = await trust_svc.list_revocations(
        processed=processed, page=page, per_page=per_page
    )
    return {
        "data": [
            RevocationResponse(
                id=r.id,
                instance_id=r.instance_id,
                revocation_type=r.revocation_type.value,
                target_type=r.target_type,
                target_id=r.target_id,
                reason=r.reason,
                revoked_at=r.revoked_at,
                processed=r.processed,
                processed_at=r.processed_at,
            )
            for r in revocations
        ],
        "meta": PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page < total)
        ),
    }


# ── Incidents (admin) ───────────────────────────────────


@router.get(
    "/federation/incidents",
    response_model=ListResponse[PeerIncidentResponse],
    tags=["federation"],
)
async def list_incidents(
    instance_id: str | None = Query(None),
    unresolved_only: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    trust_svc = FederationTrustService(db)
    incidents, total = await trust_svc.list_incidents(
        instance_id=instance_id,
        unresolved_only=unresolved_only,
        page=page,
        per_page=per_page,
    )
    return {
        "data": [
            PeerIncidentResponse(
                id=i.id,
                instance_id=i.instance_id,
                incident_type=i.incident_type.value,
                severity=i.severity.value,
                description=i.description,
                envelope_id=i.envelope_id,
                created_at=i.created_at,
                resolved_at=i.resolved_at,
                resolved_by=i.resolved_by,
            )
            for i in incidents
        ],
        "meta": PaginationMeta(
            total=total, page=page, per_page=per_page, has_more=(page * per_page < total)
        ),
    }


@router.patch(
    "/federation/incidents/{incident_id}",
    response_model=DataResponse[PeerIncidentResponse],
    tags=["federation"],
)
async def resolve_incident(
    incident_id: str,
    body: ResolveIncidentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.ADMIN)),
):
    trust_svc = FederationTrustService(db)
    incident = await trust_svc.resolve_incident(incident_id, resolved_by=user.id)
    return {
        "data": PeerIncidentResponse(
            id=incident.id,
            instance_id=incident.instance_id,
            incident_type=incident.incident_type.value,
            severity=incident.severity.value,
            description=incident.description,
            envelope_id=incident.envelope_id,
            created_at=incident.created_at,
            resolved_at=incident.resolved_at,
            resolved_by=incident.resolved_by,
        )
    }
