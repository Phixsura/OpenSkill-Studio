"""Saved search service — persistent searches with re-run for talent rediscovery.

Supports two search types:
  - "candidate": uses TalentMatchingService to find candidates matching criteria
  - "opportunity": uses OpportunitySearchService for full-text + faceted search
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.saved_search import (
    NOTIFY_FREQUENCIES,
    SEARCH_TYPES,
    SavedSearch,
)


class SavedSearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        org_id: str,
        name: str,
        search_type: str,
        search_criteria: dict,
        notify_frequency: str = "never",
        description: str | None = None,
        created_by: str,
    ) -> SavedSearch:
        if search_type not in SEARCH_TYPES:
            raise ValueError(f"search_type must be one of {sorted(SEARCH_TYPES)}")
        if notify_frequency not in NOTIFY_FREQUENCIES:
            raise ValueError(
                f"notify_frequency must be one of {sorted(NOTIFY_FREQUENCIES)}"
            )

        search = SavedSearch(
            org_id=org_id,
            name=name,
            description=description,
            search_type=search_type,
            search_criteria=search_criteria,
            notify_frequency=notify_frequency,
            created_by=created_by,
        )
        self.db.add(search)
        await self.db.flush()
        return search

    async def get(self, search_id: str) -> SavedSearch | None:
        """Execute get."""
        return await self.db.get(SavedSearch, search_id)

    async def list_searches(
        self,
        org_id: str,
        *,
        search_type: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[SavedSearch], bool]:
        q = select(SavedSearch).where(SavedSearch.org_id == org_id)
        if search_type:
            q = q.where(SavedSearch.search_type == search_type)
        if cursor:
            q = q.where(SavedSearch.id < cursor)

        q = q.order_by(SavedSearch.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())

        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def update(self, search_id: str, **fields: object) -> SavedSearch | None:
        """Execute update."""
        search = await self.db.get(SavedSearch, search_id)
        if not search:
            return None
        for key, value in fields.items():
            if hasattr(search, key) and value is not None:
                setattr(search, key, value)
        await self.db.flush()
        return search

    async def delete_search(self, search_id: str) -> bool:
        """Execute delete search."""
        result = await self.db.execute(
            delete(SavedSearch).where(SavedSearch.id == search_id)
        )
        await self.db.flush()
        return (result.rowcount or 0) > 0

    async def run_search(self, search_id: str) -> dict:
        """Execute the saved search and return fresh results.

        For candidate searches: uses matching criteria to find candidates.
        For opportunity searches: uses full-text + faceted search.
        Updates last_run_at and result_count on the saved search.
        """
        search = await self.get(search_id)
        if not search:
            return {"results": [], "result_count": 0}

        criteria = search.search_criteria
        results: list[dict] = []

        if search.search_type == "candidate":
            results = await self._run_candidate_search(criteria, search.org_id)
        else:
            results = await self._run_opportunity_search(criteria)

        # Update metadata
        search.last_run_at = datetime.now(UTC)
        search.result_count = len(results)
        await self.db.flush()

        return {"results": results, "result_count": len(results)}

    async def _run_candidate_search(self, criteria: dict, search_org_id: str) -> list[dict]:
        """Run a candidate search using the matching service.

        Enforces that the referenced opportunity belongs to the saved search's
        org to prevent cross-tenant IDOR.
        """
        opportunity_id = criteria.get("opportunity_id")
        if not opportunity_id:
            return []

        from app.talent.models.employer import Opportunity

        opp = await self.db.get(Opportunity, opportunity_id)
        if not opp or opp.employer_org_id != search_org_id:
            return []

        import dataclasses

        from app.talent.services.talent_matching import TalentMatchingService

        svc = TalentMatchingService(self.db)
        matches = await svc.match_candidates_for_opportunity(
            opportunity_id=opportunity_id,
            employer_org_id=opp.employer_org_id,
            limit=criteria.get("limit", 50),
        )
        return [dataclasses.asdict(m) for m in matches]

    async def _run_opportunity_search(self, criteria: dict) -> list[dict]:
        """Run an opportunity search using the search service."""
        from app.talent.services.opportunity_search import OpportunitySearchService

        svc = OpportunitySearchService()
        items, _has_more = await svc.search(
            self.db,
            q=criteria.get("q"),
            capability_ids=criteria.get("capability_ids"),
            opportunity_type=criteria.get("opportunity_type"),
            location_mode=criteria.get("location_mode"),
            limit=criteria.get("limit", 50),
        )
        return [
            {
                "id": o.id,
                "title": o.title,
                "opportunity_type": o.opportunity_type,
                "status": o.status,
            }
            for o in items
        ]
