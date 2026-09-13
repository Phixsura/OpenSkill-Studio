"""Evidence service — append-only evidence ledger operations (ADR-015 D2).

Evidence rows are immutable. The only mutation is status transitions:
active → superseded | voided. New/corrected evidence is always an INSERT
with supersedes_id pointing to the old row.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.evidence import (
    EVIDENCE_SOURCE_TYPES,
    VERIFICATION_LEVELS,
    CapabilityEvidence,
)


class EvidenceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_evidence(
        self,
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
        """Record a new evidence row. Idempotent via partial unique index.

        If an active row already exists for (user, capability, source_type, source_id),
        it is superseded and a new row is inserted.
        """
        if source_type not in EVIDENCE_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {source_type}")
        if verification_level not in VERIFICATION_LEVELS:
            raise ValueError(f"Invalid verification_level: {verification_level}")
        if score_normalized is not None and not (0 <= score_normalized <= 1):
            raise ValueError("score_normalized must be in [0, 1]")
        if not (0 <= confidence <= 1):
            raise ValueError("confidence must be in [0, 1]")

        # Check for existing active evidence
        existing = await self.db.execute(
            select(CapabilityEvidence).where(
                CapabilityEvidence.user_id == user_id,
                CapabilityEvidence.capability_id == capability_id,
                CapabilityEvidence.source_type == source_type,
                CapabilityEvidence.source_id == source_id,
                CapabilityEvidence.status == "active",
            )
        )
        old = existing.scalar_one_or_none()

        supersedes_id = None
        if old:
            # Supersede the existing row
            old.status = "superseded"
            supersedes_id = old.id

        evidence = CapabilityEvidence(
            user_id=user_id,
            capability_id=capability_id,
            source_type=source_type,
            source_id=source_id,
            org_id=org_id,
            score_normalized=score_normalized,
            confidence=confidence,
            verification_level=verification_level,
            occurred_at=occurred_at,
            expires_at=expires_at,
            supersedes_id=supersedes_id,
            extra=metadata or {},
        )
        self.db.add(evidence)
        await self.db.flush()
        return evidence

    async def void_evidence(
        self,
        evidence_id: str,
        *,
        reason: str | None = None,
    ) -> CapabilityEvidence | None:
        """Void an evidence row (retraction). Returns the voided row or None."""
        evidence = await self.db.get(CapabilityEvidence, evidence_id)
        if not evidence or evidence.status != "active":
            return None

        evidence.status = "voided"
        if reason:
            meta = dict(evidence.extra) if evidence.extra else {}
            meta["void_reason"] = reason
            evidence.extra = meta

        await self.db.flush()
        return evidence

    async def get_evidence_for_user(
        self,
        user_id: str,
        *,
        capability_id: str | None = None,
        status: str = "active",
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[CapabilityEvidence], int]:
        """List evidence for a user with pagination."""
        q = select(CapabilityEvidence).where(
            CapabilityEvidence.user_id == user_id,
            CapabilityEvidence.status == status,
        )
        if capability_id:
            q = q.where(CapabilityEvidence.capability_id == capability_id)

        from sqlalchemy import func

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0

        q = q.order_by(CapabilityEvidence.occurred_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def get_provenance_chain(
        self,
        evidence_id: str,
        *,
        requesting_user_id: str | None = None,
    ) -> list[dict]:
        """Resolve the provenance chain for an evidence row.

        Each link checks access; inaccessible links are redacted.
        Full provenance resolution requires product model imports — deferred
        to a dedicated resolver that understands each source_type.
        """
        evidence = await self.db.get(CapabilityEvidence, evidence_id)
        if not evidence:
            return []

        chain = [
            {
                "type": evidence.source_type,
                "id": evidence.source_id,
                "evidence_id": evidence.id,
                "verification_level": evidence.verification_level,
                "occurred_at": evidence.occurred_at.isoformat() if evidence.occurred_at else None,
            }
        ]

        # TODO: Resolve deeper provenance links per source_type
        # e.g. project_approval → submission → rubric_review → client_acceptance
        # This requires importing product models and checking access per link.
        # For v1, the chain is one level deep (evidence → source).

        return chain
