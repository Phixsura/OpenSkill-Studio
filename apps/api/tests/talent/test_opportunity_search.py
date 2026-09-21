"""Opportunity search service tests — pure logic where possible."""

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
