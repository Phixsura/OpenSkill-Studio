"""Tests for Endpoint Tag Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_tag_manager import TagManager


class TestTagManager:
    def test_add_and_get_tags(self):
        svc = TagManager()
        svc.add_tag("ep1", "auth")
        svc.add_tag("ep1", "users")
        tags = svc.get_endpoint_tags("ep1")
        assert tags == ["auth", "users"]

    def test_find_by_tag(self):
        svc = TagManager()
        svc.add_tag("ep1", "auth")
        svc.add_tag("ep2", "auth")
        svc.add_tag("ep3", "billing")
        assert svc.find_by_tag("auth") == ["ep1", "ep2"]

    def test_find_by_tags_any(self):
        svc = TagManager()
        svc.add_tag("ep1", "auth")
        svc.add_tag("ep2", "billing")
        svc.add_tag("ep3", "users")
        result = svc.find_by_tags(["auth", "billing"], match_all=False)
        assert "ep1" in result and "ep2" in result

    def test_find_by_tags_all(self):
        svc = TagManager()
        svc.add_tag("ep1", "auth")
        svc.add_tag("ep1", "v2")
        svc.add_tag("ep2", "auth")
        result = svc.find_by_tags(["auth", "v2"], match_all=True)
        assert result == ["ep1"]

    def test_remove_tag(self):
        svc = TagManager()
        svc.add_tag("ep1", "temp")
        svc.remove_tag("ep1", "temp")
        assert svc.get_endpoint_tags("ep1") == []

    def test_merge_tags(self):
        svc = TagManager()
        svc.add_tag("ep1", "old-name")
        svc.add_tag("ep2", "old-name")
        result = svc.merge_tags("old-name", "new-name")
        assert result["endpoints_updated"] == 2
        assert svc.find_by_tag("new-name") == ["ep1", "ep2"]
        assert svc.find_by_tag("old-name") == []

    def test_list_tags(self):
        svc = TagManager()
        svc.add_tag("ep1", "auth")
        svc.add_tag("ep2", "auth")
        svc.add_tag("ep1", "users")
        tags = svc.list_tags()
        assert tags[0]["tag"] == "auth"
        assert tags[0]["endpoint_count"] == 2

    def test_tag_cloud(self):
        svc = TagManager()
        svc.add_tag("ep1", "api")
        svc.add_tag("ep2", "api")
        cloud = svc.get_tag_cloud()
        assert cloud["api"] == 2

    def test_invalid_tag(self):
        svc = TagManager()
        with pytest.raises(ValueError):
            svc.add_tag("ep1", "Invalid Tag!")

    def test_tag_metadata(self):
        svc = TagManager()
        svc.add_tag("ep1", "core")
        svc.set_tag_metadata("core", description="Core APIs", color="#blue")
        tags = svc.list_tags()
        assert tags[0]["description"] == "Core APIs"

    def test_stats(self):
        svc = TagManager()
        svc.add_tag("ep1", "a")
        svc.add_tag("ep1", "b")
        svc.add_tag("ep2", "a")
        stats = svc.get_stats()
        assert stats["unique_tags"] == 2
        assert stats["total_endpoints"] == 2

    def test_isolation(self):
        a, b = TagManager(), TagManager()
        a.add_tag("ep1", "test")
        assert b.find_by_tag("test") == []
