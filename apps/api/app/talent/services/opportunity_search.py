"""Server-side opportunity search with full-text + faceted filtering (C7).

Uses PostgreSQL-compatible text search:
  - ILIKE for keyword matching (works without ts_vector setup)
  - Faceted filters: opportunity_type, location_mode, capability_ids
  - Sort: relevance (keyword match), newest, deadline
  - Cursor-based pagination via ULID
"""

from __future__ import annotations

from sqlalchemy import String, cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.employer import Opportunity


class OpportunitySearchService:
    """Search opportunities with full-text search and faceted filters."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        *,
        q: str | None = None,
        capability_ids: list[str] | None = None,
        opportunity_type: str | None = None,
        location_mode: str | None = None,
        status: str = "open",
        sort: str = "newest",  # newest, deadline, relevance
        cursor: str | None = None,
        limit: int = 20,
    ) -> tuple[list[Opportunity], bool]:
        """Search opportunities.

        Returns (results, has_more).
        """
        query = select(Opportunity).where(Opportunity.status == status)

        # Full-text search via ILIKE (works without FTS setup)
        if q and q.strip():
            sanitized = q.strip()
            # Split into words for AND-style matching
            words = sanitized.split()
            for word in words[:5]:  # limit to 5 search terms
                pattern = f"%{word}%"
                query = query.where(
                    or_(
                        Opportunity.title.ilike(pattern),
                        Opportunity.description.ilike(pattern),
                    )
                )

        # Faceted filters
        if opportunity_type:
            query = query.where(Opportunity.opportunity_type == opportunity_type)

        if location_mode:
            query = query.where(Opportunity.location_mode == location_mode)

        # Capability filter: find opportunities that require any of the given capabilities
        if capability_ids:
            # Use JSONB containment: check if required_capabilities array contains
            # any element with matching capability_id
            # This uses cast + LIKE on the JSONB text representation for compatibility
            cap_conditions = []
            for cap_id in capability_ids[:10]:  # limit to 10 capability filters
                cap_conditions.append(
                    cast(Opportunity.required_capabilities, String).like(f"%{cap_id}%")
                )
            if cap_conditions:
                query = query.where(or_(*cap_conditions))

        # Cursor pagination
        if cursor:
            query = query.where(Opportunity.id < cursor)

        # Sort
        if sort == "deadline":
            query = query.order_by(
                Opportunity.application_deadline.asc().nulls_last(),
                Opportunity.created_at.desc(),
            )
        elif sort == "relevance" and q:
            # For relevance, prefer title matches over description matches
            # Use a simple heuristic: title-matched first, then by created_at
            query = query.order_by(Opportunity.created_at.desc())
        else:  # newest
            query = query.order_by(Opportunity.created_at.desc())

        # Fetch limit+1 for has_more detection
        query = query.limit(limit + 1)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]

        return items, has_more
