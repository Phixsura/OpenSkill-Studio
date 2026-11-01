"""Tests for Consumer API Endpoint Registry service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_endpoint_registry import (
    EndpointRegistry, EndpointMeta,
)


class TestEndpointRegistry:
    def test_register_and_get(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/users", "GET", "v1", owner_team="backend"))
        ep = svc.get("ep1")
        assert ep is not None
        assert ep["path"] == "/api/users"

    def test_search_by_query(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/users", "GET", "v1", description="List users"))
        svc.register(EndpointMeta("ep2", "/api/orders", "GET", "v1", description="List orders"))
        results = svc.search(query="users")
        assert len(results) == 1

    def test_search_by_tag(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1", tags=["auth"]))
        svc.register(EndpointMeta("ep2", "/api/b", "POST", "v1", tags=["billing"]))
        results = svc.search(tag="auth")
        assert len(results) == 1

    def test_search_by_status(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1"))
        svc.register(EndpointMeta("ep2", "/api/b", "GET", "v1", status="deprecated"))
        results = svc.search(status="deprecated")
        assert len(results) == 1

    def test_update(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1"))
        svc.update("ep1", status="deprecated", description="Old")
        ep = svc.get("ep1")
        assert ep["status"] == "deprecated"

    def test_deregister(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1"))
        svc.deregister("ep1")
        assert svc.get("ep1") is None

    def test_get_by_team(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1", owner_team="backend"))
        svc.register(EndpointMeta("ep2", "/api/b", "POST", "v1", owner_team="frontend"))
        assert len(svc.get_by_team("backend")) == 1

    def test_stats(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1", owner_team="t1"))
        svc.register(EndpointMeta("ep2", "/api/b", "POST", "v1", owner_team="t2", status="beta"))
        stats = svc.get_stats()
        assert stats["total"] == 2
        assert stats["teams"] == 2

    def test_invalid_status(self):
        svc = EndpointRegistry()
        with pytest.raises(ValueError):
            svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1", status="unknown"))

    def test_invalid_path(self):
        svc = EndpointRegistry()
        with pytest.raises(ValueError):
            svc.register(EndpointMeta("ep1", "no-slash", "GET", "v1"))

    def test_duplicate(self):
        svc = EndpointRegistry()
        svc.register(EndpointMeta("ep1", "/api/a", "GET", "v1"))
        with pytest.raises(ValueError):
            svc.register(EndpointMeta("ep1", "/api/b", "POST", "v1"))

    def test_isolation(self):
        a, b = EndpointRegistry(), EndpointRegistry()
        a.register(EndpointMeta("ep1", "/api/a", "GET", "v1"))
        assert b.get("ep1") is None
