"""Talent pool, outreach, and outcome event services (ADR-015 D13, D10).

Pools: consent-based grouping. Rule-suggested = pending until user accepts.
Outreach: anti-spam rate limited (max 3 per org→user per 30 days).
Outcomes: longitudinal career events with user-controlled visibility.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.internship import OUTCOME_EVENT_TYPES, OutcomeEvent
from app.talent.models.talent_pool import (
    TalentOutreach,
    TalentPool,
    TalentPoolMembership,
)

# Anti-spam: max outreach from one org to one user within this window
OUTREACH_RATE_WINDOW_DAYS = 30
OUTREACH_RATE_LIMIT = 3


# ---------------------------------------------------------------------------
# Talent Pool
# ---------------------------------------------------------------------------


class TalentPoolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pool(
        self,
        *,
        org_id: str,
        name: str,
        description: str | None = None,
        membership_mode: str = "manual",
        rule_config: dict | None = None,
        visibility: str = "internal",
        created_by: str | None = None,
    ) -> TalentPool:
        if membership_mode not in ("manual", "rule_suggested", "candidate_opt_in"):
            raise ValueError(f"Invalid membership_mode: {membership_mode}")
        if visibility not in ("internal", "shared"):
            raise ValueError(f"Invalid visibility: {visibility}")

        pool = TalentPool(
            org_id=org_id,
            name=name,
            description=description,
            membership_mode=membership_mode,
            rule_config=rule_config,
            visibility=visibility,
            created_by=created_by,
        )
        self.db.add(pool)
        await self.db.flush()
        return pool

    async def get_pool(self, pool_id: str) -> TalentPool | None:
        """Execute get pool."""
        return await self.db.get(TalentPool, pool_id)

    async def list_pools(
        self,
        org_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        cursor: str | None = None,
    ) -> tuple[list[TalentPool], int]:
        q = select(TalentPool).where(TalentPool.org_id == org_id)
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0
        q = q.order_by(TalentPool.created_at.desc()).limit(limit + 1 if cursor is not None else limit).offset(0 if cursor is not None else offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update_pool(self, pool_id: str, **fields) -> TalentPool | None:
        """Execute update pool."""
        pool = await self.db.get(TalentPool, pool_id)
        if not pool:
            return None
        for key, value in fields.items():
            if hasattr(pool, key):
                setattr(pool, key, value)
        await self.db.flush()
        return pool

    async def add_member(
        self,
        pool_id: str,
        user_id: str,
        source: str,
        added_by: str | None = None,
    ) -> TalentPoolMembership:
        if source not in ("manual_added", "rule_suggested", "opted_in"):
            raise ValueError(f"Invalid source: {source}")

        # Consent logic:
        # - opted_in: only allowed when the acting user IS the target user
        #   (self opt-in). Org members cannot set opted_in for others.
        # - manual_added: requires explicit user consent (pending_consent)
        # - rule_suggested: requires explicit user consent (pending_consent)
        if source == "opted_in" and added_by != user_id:
            raise ValueError("Only the user themselves can opt into a pool")

        consent = "accepted" if source == "opted_in" else "pending_consent"

        membership = TalentPoolMembership(
            pool_id=pool_id,
            user_id=user_id,
            source=source,
            consent_status=consent,
            added_by=added_by,
        )
        self.db.add(membership)
        await self.db.flush()
        return membership

    async def respond_to_membership(
        self,
        membership_id: str,
        user_id: str,
        *,
        accept: bool,
    ) -> TalentPoolMembership | None:
        membership = await self.db.get(TalentPoolMembership, membership_id)
        if not membership:
            return None
        # Only the member user can respond
        if membership.user_id != user_id:
            return None
        if membership.consent_status not in ("pending_consent",):
            raise ValueError("Membership is not pending consent")

        membership.consent_status = "accepted" if accept else "declined"
        await self.db.flush()
        return membership

    async def list_members(
        self,
        pool_id: str,
        *,
        consent_status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        cursor: str | None = None,
    ) -> tuple[list[TalentPoolMembership], int]:
        q = select(TalentPoolMembership).where(TalentPoolMembership.pool_id == pool_id)
        if consent_status:
            q = q.where(TalentPoolMembership.consent_status == consent_status)
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0
        q = q.order_by(TalentPoolMembership.created_at.desc()).limit(limit + 1 if cursor is not None else limit).offset(0 if cursor is not None else offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def remove_member(self, pool_id: str, user_id: str) -> bool:
        """Execute remove member."""
        result = await self.db.execute(
            delete(TalentPoolMembership).where(
                TalentPoolMembership.pool_id == pool_id,
                TalentPoolMembership.user_id == user_id,
            )
        )
        await self.db.flush()
        return (result.rowcount or 0) > 0


# ---------------------------------------------------------------------------
# Outreach
# ---------------------------------------------------------------------------


class OutreachService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_outreach(
        self,
        *,
        org_id: str,
        user_id: str,
        outreach_type: str,
        target_type: str,
        target_id: str,
        message: str | None = None,
        expires_at: datetime | None = None,
    ) -> TalentOutreach:
        if outreach_type not in ("opportunity_invitation", "pool_invitation"):
            raise ValueError(f"Invalid outreach_type: {outreach_type}")

        # Anti-spam: max OUTREACH_RATE_LIMIT per (org, user) within window
        cutoff = datetime.now(UTC) - timedelta(days=OUTREACH_RATE_WINDOW_DAYS)
        count_q = select(func.count()).select_from(
            select(TalentOutreach.id)
            .where(
                TalentOutreach.org_id == org_id,
                TalentOutreach.user_id == user_id,
                TalentOutreach.created_at >= cutoff,
            )
            .subquery()
        )
        recent_count = (await self.db.execute(count_q)).scalar() or 0
        if recent_count >= OUTREACH_RATE_LIMIT:
            raise ValueError(
                f"OUTREACH_RATE_LIMITED: Max {OUTREACH_RATE_LIMIT} outreach "
                f"per organization per user within {OUTREACH_RATE_WINDOW_DAYS} days"
            )

        outreach = TalentOutreach(
            org_id=org_id,
            user_id=user_id,
            outreach_type=outreach_type,
            target_type=target_type,
            target_id=target_id,
            message=message,
            expires_at=expires_at,
        )
        self.db.add(outreach)
        await self.db.flush()
        return outreach

    async def respond_to_outreach(
        self,
        outreach_id: str,
        user_id: str,
        *,
        status: str,
    ) -> TalentOutreach | None:
        if status not in ("accepted", "declined"):
            raise ValueError(f"Invalid response status: {status}. Must be 'accepted' or 'declined'")

        outreach = await self.db.get(TalentOutreach, outreach_id)
        if not outreach:
            return None
        # Only the target user can respond
        if outreach.user_id != user_id:
            return None
        if outreach.status not in ("sent", "viewed"):
            raise ValueError(f"Cannot respond to outreach in status '{outreach.status}'")

        outreach.status = status
        outreach.responded_at = datetime.now(UTC)
        await self.db.flush()
        return outreach

    async def list_outreach(
        self,
        *,
        org_id: str | None = None,
        user_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        cursor: str | None = None,
    ) -> tuple[list[TalentOutreach], int]:
        q = select(TalentOutreach)
        if org_id:
            q = q.where(TalentOutreach.org_id == org_id)
        if user_id:
            q = q.where(TalentOutreach.user_id == user_id)
        if status:
            q = q.where(TalentOutreach.status == status)
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0
        q = q.order_by(TalentOutreach.created_at.desc()).limit(limit + 1 if cursor is not None else limit).offset(0 if cursor is not None else offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total


# ---------------------------------------------------------------------------
# Outcome Events
# ---------------------------------------------------------------------------


class OutcomeEventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_event(
        self,
        *,
        user_id: str,
        event_type: str,
        occurred_at: datetime,
        source_type: str | None = None,
        source_id: str | None = None,
        visibility: str = "private",
        metadata: dict | None = None,
    ) -> OutcomeEvent:
        if event_type not in OUTCOME_EVENT_TYPES:
            raise ValueError(f"Invalid event_type: {event_type}. Must be one of {sorted(OUTCOME_EVENT_TYPES)}")
        if visibility not in ("private", "passport_visible", "public"):
            raise ValueError(f"Invalid visibility: {visibility}")

        event = OutcomeEvent(
            user_id=user_id,
            event_type=event_type,
            source_type=source_type,
            source_id=source_id,
            visibility=visibility,
            extra=metadata or {},
            occurred_at=occurred_at,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def list_events(
        self,
        user_id: str,
        *,
        event_type: str | None = None,
        visibility: str | None = None,
        limit: int = 50,
        offset: int = 0,
        cursor: str | None = None,
    ) -> tuple[list[OutcomeEvent], int]:
        q = select(OutcomeEvent).where(OutcomeEvent.user_id == user_id)
        if event_type:
            q = q.where(OutcomeEvent.event_type == event_type)
        if visibility:
            q = q.where(OutcomeEvent.visibility == visibility)
        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0
        q = q.order_by(OutcomeEvent.occurred_at.desc()).limit(limit + 1 if cursor is not None else limit).offset(0 if cursor is not None else offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update_visibility(
        self,
        event_id: str,
        user_id: str,
        visibility: str,
    ) -> OutcomeEvent | None:
        if visibility not in ("private", "passport_visible", "public"):
            raise ValueError(f"Invalid visibility: {visibility}")
        event = await self.db.get(OutcomeEvent, event_id)
        if not event:
            return None
        if event.user_id != user_id:
            return None
        event.visibility = visibility
        await self.db.flush()
        return event

    async def auto_generate_placement_event(
        self,
        *,
        user_id: str,
        placement_id: str,
        event_type: str,
        occurred_at: datetime,
    ) -> OutcomeEvent:
        """Auto-generate an outcome event when a placement status changes.

        Auto-generated events default to private — the user must explicitly
        change visibility.
        """
        return await self.record_event(
            user_id=user_id,
            event_type=event_type,
            source_type="placement",
            source_id=placement_id,
            occurred_at=occurred_at,
            visibility="private",
        )
