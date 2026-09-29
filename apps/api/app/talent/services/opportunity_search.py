"""Server-side opportunity search with full-text + faceted filtering (C7).

Uses PostgreSQL-compatible text search:
  - ILIKE for keyword matching (works without ts_vector setup)
  - Faceted filters: opportunity_type, location_mode, capability_ids
  - Sort: relevance (keyword match), newest, deadline
  - Cursor-based pagination via ULID
"""

from __future__ import annotations

from sqlalchemy import String, and_, cast, or_, select
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
                # R394: escape LIKE metacharacters — a raw `_`/`%` in the query
                # acts as a wildcard ("a_b" matched "aXb"; "%%" matched all)
                escaped = word.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
                pattern = f"%{escaped}%"
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
                    cast(Opportunity.required_capabilities, String).like(
                        f"%{cap_id.replace(chr(37), '').replace('_', '')}%"
                    )
                )
            if cap_conditions:
                query = query.where(or_(*cap_conditions))

        # R395: the cursor predicate must match the SORT ORDER — `id < cursor`
        # under a deadline ordering dropped arbitrary rows on page 2 (any id
        # above the last page's floor vanished regardless of deadline), and
        # under created_at ordering tied timestamps could skip rows. Newest/
        # relevance now order strictly by id (ULIDs are time-ordered, so this
        # IS newest-first); deadline uses a composite keyset token.
        if sort == "deadline":
            if cursor:
                from datetime import datetime as _dt

                kind, _, rest = cursor.partition("|")
                if kind == "d":
                    iso, _, last_id = rest.partition("|")
                    pivot = _dt.fromisoformat(iso)
                    query = query.where(
                        or_(
                            Opportunity.application_deadline > pivot,
                            and_(
                                Opportunity.application_deadline == pivot,
                                Opportunity.id < last_id,
                            ),
                            Opportunity.application_deadline.is_(None),
                        )
                    )
                elif kind == "n":
                    query = query.where(
                        Opportunity.application_deadline.is_(None),
                        Opportunity.id < rest,
                    )
                else:  # legacy bare-id cursor: best-effort id floor
                    query = query.where(Opportunity.id < cursor)
            query = query.order_by(
                Opportunity.application_deadline.asc().nulls_last(),
                Opportunity.id.desc(),
            )
        else:  # newest / relevance — strict ULID order == creation order
            if cursor:
                last_id = cursor.rpartition("|")[2]
                query = query.where(Opportunity.id < last_id)
            query = query.order_by(Opportunity.id.desc())

        # Fetch limit+1 for has_more detection
        query = query.limit(limit + 1)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]

        next_cursor = None
        if has_more and items:
            last = items[-1]
            if sort == "deadline":
                next_cursor = (
                    f"d|{last.application_deadline.isoformat()}|{last.id}"
                    if last.application_deadline is not None
                    else f"n|{last.id}"
                )
            else:
                next_cursor = last.id
        return items, has_more, next_cursor
