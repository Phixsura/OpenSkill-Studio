"""Federation Exchange service (Issue #45 Parts D–J).

Cross-instance artifact exchange, credential verification, talent mobility,
opportunity/marketplace/ecosystem federation, and federated search.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.federation import (
    DataResidencyPolicy,
    FederatedAccountLink,
    FederatedArtifact,
    FederatedCredentialVerification,
    FederatedEcosystemObservation,
    FederatedMarketplaceListing,
    FederatedOpportunity,
    FederationSearchCache,
    PortabilityRecord,
)


class PeerNotFoundError(AppError):
    def __init__(self):
        super().__init__("PEER_NOT_FOUND", "Federation peer not found", 404)


class ArtifactNotFoundError(AppError):
    def __init__(self):
        super().__init__("ARTIFACT_NOT_FOUND", "Federated artifact not found", 404)


# ── Part D: Cross-instance Registry (Artifact Exchange) ─────────────


async def publish_artifact(
    db: AsyncSession,
    org_id: str,
    *,
    artifact_type: str,
    artifact_id: str,
    version: str,
    manifest: dict,
    checksum: str,
    signature: str | None = None,
    target_instance_id: str | None = None,
) -> FederatedArtifact:
    artifact = FederatedArtifact(
        org_id=org_id,
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        version=version,
        manifest=manifest,
        checksum=checksum,
        signature=signature,
        target_instance_id=target_instance_id,
        status="published",
    )
    db.add(artifact)
    await db.flush()
    return artifact


async def list_artifacts(
    db: AsyncSession,
    org_id: str,
    *,
    artifact_type: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[FederatedArtifact], int]:
    base = select(FederatedArtifact).where(FederatedArtifact.org_id == org_id)
    count_q = select(func.count()).select_from(FederatedArtifact).where(FederatedArtifact.org_id == org_id)

    if artifact_type:
        base = base.where(FederatedArtifact.artifact_type == artifact_type)
        count_q = count_q.where(FederatedArtifact.artifact_type == artifact_type)
    if status:
        base = base.where(FederatedArtifact.status == status)
        count_q = count_q.where(FederatedArtifact.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederatedArtifact.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


async def get_artifact(
    db: AsyncSession, artifact_id: str, org_id: str,
) -> FederatedArtifact:
    result = await db.execute(
        select(FederatedArtifact).where(
            FederatedArtifact.id == artifact_id,
            FederatedArtifact.org_id == org_id,
        )
    )
    artifact = result.scalar_one_or_none()
    if artifact is None:
        raise ArtifactNotFoundError()
    return artifact


# ── Part E: Credential / Passport Verification ──────────────────────


async def create_credential_verification(
    db: AsyncSession,
    org_id: str,
    *,
    user_id: str,
    credential_type: str,
    credential_id: str,
    issuer_instance_id: str,
    verification_data: dict,
) -> FederatedCredentialVerification:
    verification = FederatedCredentialVerification(
        org_id=org_id,
        user_id=user_id,
        credential_type=credential_type,
        credential_id=credential_id,
        issuer_instance_id=issuer_instance_id,
        verification_data=verification_data,
        status="pending",
    )
    db.add(verification)
    await db.flush()
    return verification


async def list_credential_verifications(
    db: AsyncSession,
    org_id: str,
    *,
    user_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[FederatedCredentialVerification], int]:
    base = select(FederatedCredentialVerification).where(FederatedCredentialVerification.org_id == org_id)
    count_q = select(func.count()).select_from(FederatedCredentialVerification).where(FederatedCredentialVerification.org_id == org_id)

    if user_id:
        base = base.where(FederatedCredentialVerification.user_id == user_id)
        count_q = count_q.where(FederatedCredentialVerification.user_id == user_id)
    if status:
        base = base.where(FederatedCredentialVerification.status == status)
        count_q = count_q.where(FederatedCredentialVerification.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederatedCredentialVerification.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Part F: Talent Mobility ──────────────────────────────────────────


async def create_account_link(
    db: AsyncSession,
    org_id: str,
    *,
    user_id: str,
    remote_instance_id: str,
    remote_user_ref: str,
    link_type: str = "portable_profile",
) -> FederatedAccountLink:
    link = FederatedAccountLink(
        org_id=org_id,
        user_id=user_id,
        remote_instance_id=remote_instance_id,
        remote_user_ref=remote_user_ref,
        link_type=link_type,
        status="active",
    )
    db.add(link)
    await db.flush()
    return link


async def list_account_links(
    db: AsyncSession,
    org_id: str,
    *,
    user_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[FederatedAccountLink], int]:
    base = select(FederatedAccountLink).where(FederatedAccountLink.org_id == org_id)
    count_q = select(func.count()).select_from(FederatedAccountLink).where(FederatedAccountLink.org_id == org_id)

    if user_id:
        base = base.where(FederatedAccountLink.user_id == user_id)
        count_q = count_q.where(FederatedAccountLink.user_id == user_id)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederatedAccountLink.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


async def create_portability_record(
    db: AsyncSession,
    org_id: str,
    *,
    user_id: str,
    record_type: str,
    source_instance_id: str,
    destination_instance_id: str,
    data_manifest: dict,
) -> PortabilityRecord:
    record = PortabilityRecord(
        org_id=org_id,
        user_id=user_id,
        record_type=record_type,
        source_instance_id=source_instance_id,
        destination_instance_id=destination_instance_id,
        data_manifest=data_manifest,
        status="pending",
    )
    db.add(record)
    await db.flush()
    return record


# ── Part G: Opportunity Federation ───────────────────────────────────


async def publish_opportunity(
    db: AsyncSession,
    org_id: str,
    *,
    opportunity_id: str,
    title: str,
    description: str | None = None,
    requirements: dict | None = None,
    target_instances: list | None = None,
) -> FederatedOpportunity:
    opp = FederatedOpportunity(
        org_id=org_id,
        opportunity_id=opportunity_id,
        title=title,
        description=description,
        requirements=requirements or {},
        target_instances=target_instances or [],
        status="published",
    )
    db.add(opp)
    await db.flush()
    return opp


async def list_opportunities(
    db: AsyncSession,
    org_id: str,
    *,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[FederatedOpportunity], int]:
    base = select(FederatedOpportunity).where(FederatedOpportunity.org_id == org_id)
    count_q = select(func.count()).select_from(FederatedOpportunity).where(FederatedOpportunity.org_id == org_id)

    if status:
        base = base.where(FederatedOpportunity.status == status)
        count_q = count_q.where(FederatedOpportunity.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederatedOpportunity.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Part H: Marketplace Federation ───────────────────────────────────


async def publish_listing(
    db: AsyncSession,
    org_id: str,
    *,
    listing_id: str,
    title: str,
    listing_type: str,
    price_info: dict | None = None,
    target_instances: list | None = None,
) -> FederatedMarketplaceListing:
    listing = FederatedMarketplaceListing(
        org_id=org_id,
        listing_id=listing_id,
        title=title,
        listing_type=listing_type,
        price_info=price_info or {},
        target_instances=target_instances or [],
        status="published",
    )
    db.add(listing)
    await db.flush()
    return listing


async def list_marketplace_listings(
    db: AsyncSession,
    org_id: str,
    *,
    listing_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[FederatedMarketplaceListing], int]:
    base = select(FederatedMarketplaceListing).where(FederatedMarketplaceListing.org_id == org_id)
    count_q = select(func.count()).select_from(FederatedMarketplaceListing).where(FederatedMarketplaceListing.org_id == org_id)

    if listing_type:
        base = base.where(FederatedMarketplaceListing.listing_type == listing_type)
        count_q = count_q.where(FederatedMarketplaceListing.listing_type == listing_type)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederatedMarketplaceListing.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Part I: Ecosystem Intelligence Federation ────────────────────────


async def publish_observation(
    db: AsyncSession,
    org_id: str,
    *,
    observation_type: str,
    subject_type: str,
    subject_id: str,
    data: dict,
    source_instance_id: str | None = None,
) -> FederatedEcosystemObservation:
    obs = FederatedEcosystemObservation(
        org_id=org_id,
        observation_type=observation_type,
        subject_type=subject_type,
        subject_id=subject_id,
        data=data,
        source_instance_id=source_instance_id,
        status="published",
    )
    db.add(obs)
    await db.flush()
    return obs


async def list_observations(
    db: AsyncSession,
    org_id: str,
    *,
    observation_type: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[FederatedEcosystemObservation], int]:
    base = select(FederatedEcosystemObservation).where(FederatedEcosystemObservation.org_id == org_id)
    count_q = select(func.count()).select_from(FederatedEcosystemObservation).where(FederatedEcosystemObservation.org_id == org_id)

    if observation_type:
        base = base.where(FederatedEcosystemObservation.observation_type == observation_type)
        count_q = count_q.where(FederatedEcosystemObservation.observation_type == observation_type)

    total = (await db.execute(count_q)).scalar() or 0
    result = await db.execute(
        base.order_by(FederatedEcosystemObservation.created_at.desc())
        .offset((page - 1) * per_page).limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Part J: Federated Search ─────────────────────────────────────────


async def cache_search_result(
    db: AsyncSession,
    org_id: str,
    *,
    query_hash: str,
    query_text: str,
    results: list,
    source_instances: list,
    ttl_seconds: int = 300,
) -> FederationSearchCache:
    cache = FederationSearchCache(
        org_id=org_id,
        query_hash=query_hash,
        query_text=query_text,
        results=results,
        source_instances=source_instances,
        ttl_seconds=ttl_seconds,
    )
    db.add(cache)
    await db.flush()
    return cache


async def get_cached_search(
    db: AsyncSession,
    org_id: str,
    query_hash: str,
) -> FederationSearchCache | None:
    result = await db.execute(
        select(FederationSearchCache).where(
            FederationSearchCache.org_id == org_id,
            FederationSearchCache.query_hash == query_hash,
        )
    )
    return result.scalar_one_or_none()


# ── Part M: Data Residency ───────────────────────────────────────────


async def create_residency_policy(
    db: AsyncSession,
    org_id: str,
    *,
    name: str,
    allowed_regions: list,
    blocked_regions: list | None = None,
    data_categories: list | None = None,
    enforcement_mode: str = "enforce",
) -> DataResidencyPolicy:
    policy = DataResidencyPolicy(
        org_id=org_id,
        name=name,
        allowed_regions=allowed_regions,
        blocked_regions=blocked_regions or [],
        data_categories=data_categories or [],
        enforcement_mode=enforcement_mode,
        is_active=True,
    )
    db.add(policy)
    await db.flush()
    return policy


async def list_residency_policies(
    db: AsyncSession,
    org_id: str,
) -> list[DataResidencyPolicy]:
    result = await db.execute(
        select(DataResidencyPolicy)
        .where(DataResidencyPolicy.org_id == org_id)
        .order_by(DataResidencyPolicy.created_at.desc())
    )
    return list(result.scalars().all())
