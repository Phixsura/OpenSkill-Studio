"""Talent facade — the ONLY entry point for product code (ADR-015).

Product code imports ONLY from this module. Talent code may import product
models but never product services (except evidence_ingest for provenance).
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.assessment import Credential
from app.talent.models.evidence import CapabilityEvidence
from app.talent.services.scoring import CapabilityScore, compute_capability_profile


async def record_capability_evidence(
    db: AsyncSession,
    *,
    user_id: str,
    capability_id: str,
    source_type: str,
    source_id: str,
    verification_level: str,
    occurred_at: datetime,
    org_id: str | None = None,
    score_normalized: float | None = None,
    confidence: float = 1.0,
    expires_at: datetime | None = None,
    metadata: dict | None = None,
) -> CapabilityEvidence:
    """Record a new evidence row. Idempotent on (user, cap, source_type, source_id)."""
    from app.talent.services.evidence import EvidenceService

    svc = EvidenceService(db)
    return await svc.record_evidence(
        user_id=user_id,
        capability_id=capability_id,
        source_type=source_type,
        source_id=source_id,
        verification_level=verification_level,
        occurred_at=occurred_at,
        org_id=org_id,
        score_normalized=score_normalized,
        confidence=confidence,
        expires_at=expires_at,
        metadata=metadata or {},
    )


async def get_user_capability_profile(
    db: AsyncSession,
    user_id: str,
) -> list[CapabilityScore]:
    """Return derived capability scores for a user."""
    return await compute_capability_profile(db, user_id)


async def get_passport_summary(
    db: AsyncSession,
    user_id: str,
    *,
    requesting_user_id: str | None = None,
    requesting_org_id: str | None = None,
) -> dict | None:
    """Return the passport summary respecting privacy settings.

    Returns None if the passport is private and the requestor has no access.
    """
    from app.talent.services.passport import PassportService

    svc = PassportService(db)
    return await svc.get_visible_passport(
        user_id,
        requesting_user_id=requesting_user_id,
        requesting_org_id=requesting_org_id,
    )


async def check_credential_status(
    db: AsyncSession,
    credential_id: str,
) -> dict | None:
    """Check if a credential is active. Returns status dict or None if not found."""
    row = await db.get(Credential, credential_id)
    if not row:
        return None
    return {
        "credential_id": row.id,
        "credential_type": row.credential_type,
        "status": row.status,
        "issued_at": row.issued_at.isoformat() if row.issued_at else None,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
    }
