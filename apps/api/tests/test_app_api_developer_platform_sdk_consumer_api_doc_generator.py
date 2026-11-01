"""Tests for API Documentation Generator service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_doc_generator import (
    DocGenerator, EndpointDoc, ParamSpec,
)


class TestDocGenerator:
    def test_register_and_generate(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/api/users", "GET", "List users",
                                  tags=["Users"]))
        md = svc.generate_markdown("ep1")
        assert "GET /api/users" in md
        assert "List users" in md

    def test_params_in_markdown(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/api/users/{id}", "GET", "Get user",
                                  params=[ParamSpec("id", "path", "string",
                                                    description="User ID")]))
        md = svc.generate_markdown("ep1")
        assert "| id |" in md
        assert "User ID" in md

    def test_deprecated_badge(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/api/old", "GET", "Old endpoint",
                                  deprecated=True))
        md = svc.generate_markdown("ep1")
        assert "Deprecated" in md

    def test_table_of_contents(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/api/users", "GET", "List users", tags=["Users"]))
        svc.register(EndpointDoc("ep2", "/api/orders", "POST", "Create order", tags=["Orders"]))
        toc = svc.get_table_of_contents()
        tags = [t["tag"] for t in toc]
        assert "Users" in tags
        assert "Orders" in tags

    def test_search(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/api/users", "GET", "List all users"))
        svc.register(EndpointDoc("ep2", "/api/orders", "GET", "List orders"))
        results = svc.search("users")
        assert len(results) == 1
        assert results[0]["endpoint_id"] == "ep1"

    def test_update(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/api/x", "GET", "Original"))
        svc.update("ep1", summary="Updated summary")
        md = svc.generate_markdown("ep1")
        assert "Updated summary" in md

    def test_stats(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/a", "GET", "A", tags=["T1"]))
        svc.register(EndpointDoc("ep2", "/b", "POST", "B", tags=["T2"], deprecated=True))
        stats = svc.get_stats()
        assert stats["total_endpoints"] == 2
        assert stats["deprecated"] == 1
        assert stats["unique_tags"] == 2

    def test_duplicate_rejected(self):
        svc = DocGenerator()
        svc.register(EndpointDoc("ep1", "/a", "GET", "A"))
        with pytest.raises(ValueError):
            svc.register(EndpointDoc("ep1", "/b", "POST", "B"))

    def test_empty_summary_rejected(self):
        svc = DocGenerator()
        with pytest.raises(ValueError):
            svc.register(EndpointDoc("ep1", "/a", "GET", ""))

    def test_isolation(self):
        a, b = DocGenerator(), DocGenerator()
        a.register(EndpointDoc("ep1", "/a", "GET", "A"))
        assert b.get_stats()["total_endpoints"] == 0
