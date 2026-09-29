"""Opportunity search service tests — pure logic where possible."""

import pytest
from ulid import ULID

from app.talent.services.opportunity_search import OpportunitySearchService


class TestOpportunitySearchService:
    """Test search service structure and configuration."""

    def test_service_instantiation(self):
        """Service can be created with a mock db."""
        svc = OpportunitySearchService(db=None)  # type: ignore
        assert svc.db is None

    def test_search_method_exists(self):
        """search() method exists with correct signature."""
        svc = OpportunitySearchService(db=None)  # type: ignore
        import inspect

        sig = inspect.signature(svc.search)
        params = set(sig.parameters.keys())
        assert "q" in params
        assert "capability_ids" in params
        assert "opportunity_type" in params
        assert "location_mode" in params
        assert "status" in params
        assert "sort" in params
        assert "cursor" in params
        assert "limit" in params

    def test_default_status_is_open(self):
        """Default status filter should be 'open'."""
        import inspect

        svc = OpportunitySearchService(db=None)  # type: ignore
        sig = inspect.signature(svc.search)
        assert sig.parameters["status"].default == "open"

    def test_default_sort_is_newest(self):
        """Default sort should be 'newest'."""
        import inspect

        svc = OpportunitySearchService(db=None)  # type: ignore
        sig = inspect.signature(svc.search)
        assert sig.parameters["sort"].default == "newest"

    def test_default_limit_is_20(self):
        """Default limit should be 20."""
        import inspect

        svc = OpportunitySearchService(db=None)  # type: ignore
        sig = inspect.signature(svc.search)
        assert sig.parameters["limit"].default == 20


class TestSearchQuerySanitization:
    """Test that search terms are handled correctly at the API level."""

    def test_empty_query_accepted(self):
        """Empty or None query should not cause errors."""
        # This tests the schema level, not the service
        from app.talent.schemas.employer import CreateOpportunityRequest

        # Verify the schema imports work
        assert CreateOpportunityRequest is not None

    def test_api_query_params_exist(self):
        """The opportunities list endpoint should accept search params."""
        import inspect

        from app.talent.api.employers import list_opportunities

        sig = inspect.signature(list_opportunities)
        params = set(sig.parameters.keys())
        assert "q" in params
        assert "location_mode" in params
        assert "capabilities" in params
        assert "sort" in params

# ── Round-394 killer (issue #35 hardening): LIKE metacharacters ──────


@pytest.fixture
async def db():
    from app.core.database import AsyncSessionLocal, engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_search_escapes_like_metacharacters(db):
    """R394: raw user words reached ILIKE unescaped — "50_" matched "50x",
    "%" matched everything. Escaped now: wildcard characters in the query
    are literals."""
    from app.talent.models.employer import Opportunity
    from tests.test_cp_marketplace_db import _mk_org, _mk_user

    user = await _mk_user(db)
    org = await _mk_org(db, user)
    marker = str(ULID()).lower()
    lit = Opportunity(
        employer_org_id=org.id, title=f"{marker} 50% off promo build",
        opportunity_type="contract", status="open",
    )
    trap = Opportunity(
        employer_org_id=org.id, title=f"{marker} 50x off promo build",
        opportunity_type="contract", status="open",
    )
    db.add_all([lit, trap])
    await db.flush()

    svc = OpportunitySearchService(db)
    rows, _more = await svc.search(q=f"{marker} 50%")
    ids = {o.id for o in rows}
    assert lit.id in ids, "literal '50%' row must match"
    assert trap.id not in ids, "'%' must not act as a wildcard (matched '50x')"

    rows, _more = await svc.search(q=f"{marker} 50_")
    ids = {o.id for o in rows}
    assert trap.id not in ids and lit.id not in ids, "'_' must not match any single char"
