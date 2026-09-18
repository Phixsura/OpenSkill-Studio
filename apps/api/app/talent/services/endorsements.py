"""Skill endorsement service — peer verification flow (ADR-015 upgrade).

Manages skill endorsements: create, list, summarize. Auto-generates
peer_verified evidence when an endorsement is accepted. Prevents
self-endorsement and duplicate endorsements.
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.endorsement import (
    ENDORSEMENT_RELATIONSHIPS,
    SkillEndorsement,
)


class EndorsementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def endorse(
        self,
        *,
        user_id: str,
        endorser_id: str,
        capability_id: str,
        relationship: str,
        message: str | None = None,
    ) -> SkillEndorsement:
        """Endorse a user's capability.

        Raises ValueError for self-endorsement, invalid relationship,
        or duplicate endorsement.
        """
        if user_id == endorser_id:
            raise ValueError("Cannot endorse yourself")

        if relationship not in ENDORSEMENT_RELATIONSHIPS:
            raise ValueError(
                f"Invalid relationship: {relationship}. "
                f"Must be one of {sorted(ENDORSEMENT_RELATIONSHIPS)}"
            )

        if message and len(message) > 500:
            raise ValueError("Endorsement message must be 500 characters or less")

        # Check for duplicate
        existing = await self.db.execute(
            select(SkillEndorsement).where(
                SkillEndorsement.user_id == user_id,
                SkillEndorsement.endorser_id == endorser_id,
                SkillEndorsement.capability_id == capability_id,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                "DUPLICATE_ENDORSEMENT: You have already endorsed this "
                "user for this capability"
            )

        endorsement = SkillEndorsement(
            user_id=user_id,
            endorser_id=endorser_id,
            capability_id=capability_id,
            relationship=relationship,
            message=message,
            status="accepted",
        )
        self.db.add(endorsement)
        await self.db.flush()

        # Auto-create peer_verified evidence
        from datetime import UTC, datetime

        from app.talent.models.evidence import CapabilityEvidence

        evidence = CapabilityEvidence(
            user_id=user_id,
            capability_id=capability_id,
            source_type="peer_review",
            source_id=endorsement.id,
            score_normalized=0.7,  # moderate default for peer endorsement
            confidence=0.6,
            verification_level="peer_verified",
            occurred_at=datetime.now(UTC),
        )
        self.db.add(evidence)
        await self.db.flush()

        return endorsement

    async def list_endorsements(
        self,
        user_id: str,
        *,
        capability_id: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[SkillEndorsement], bool]:
        """List endorsements received by a user."""
        q = select(SkillEndorsement).where(
            SkillEndorsement.user_id == user_id
        )
        if capability_id:
            q = q.where(SkillEndorsement.capability_id == capability_id)
        if cursor:
            q = q.where(SkillEndorsement.id < cursor)

        q = q.order_by(SkillEndorsement.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def get_endorsement_summary(self, user_id: str) -> dict:
        """Get endorsement summary: count by capability and relationship."""
        result = await self.db.execute(
            select(SkillEndorsement).where(
                SkillEndorsement.user_id == user_id
            )
        )
        endorsements = result.scalars().all()

        by_capability: dict[str, int] = defaultdict(int)
        by_relationship: dict[str, int] = defaultdict(int)
        for e in endorsements:
            by_capability[e.capability_id] += 1
            by_relationship[e.relationship] += 1

        return {
            "total": len(endorsements),
            "by_capability": dict(by_capability),
            "by_relationship": dict(by_relationship),
        }
