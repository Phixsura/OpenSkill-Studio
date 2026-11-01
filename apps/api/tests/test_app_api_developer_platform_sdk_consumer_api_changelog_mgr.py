"""Tests for Endpoint Changelog Manager service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_changelog_mgr import (
    ChangelogManager, ChangelogEntry,
)


class TestChangelogManager:
    def test_add_and_get_version(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "2.0.0", "added", "New users endpoint"))
        svc.add_entry(ChangelogEntry("e2", "2.0.0", "fixed", "Auth bug fix"))
        result = svc.get_version("2.0.0")
        assert result["entry_count"] == 2
        assert "added" in result["by_type"]

    def test_breaking_changes(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "2.0.0", "removed", "Removed v1 users", breaking=True))
        svc.add_entry(ChangelogEntry("e2", "2.0.0", "added", "New feature"))
        breaking = svc.get_breaking_changes()
        assert len(breaking) == 1
        assert svc.get_version("2.0.0")["has_breaking_changes"] is True

    def test_endpoint_history(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "1.0.0", "added", "Initial", endpoint_id="ep1"))
        svc.add_entry(ChangelogEntry("e2", "2.0.0", "changed", "Updated", endpoint_id="ep1"))
        history = svc.get_endpoint_history("ep1")
        assert len(history) == 2
        assert history[0]["version"] == "2.0.0"

    def test_list_versions(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "1.0.0", "added", "A"))
        svc.add_entry(ChangelogEntry("e2", "2.0.0", "added", "B"))
        svc.add_entry(ChangelogEntry("e3", "1.1.0", "fixed", "C"))
        versions = svc.list_versions()
        assert versions[0] == "2.0.0"

    def test_generate_markdown(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "1.0.0", "added", "New endpoint"))
        svc.add_entry(ChangelogEntry("e2", "1.0.0", "fixed", "Bug fix"))
        md = svc.generate_markdown("1.0.0")
        assert "## 1.0.0" in md
        assert "New endpoint" in md
        assert "Bug fix" in md

    def test_search(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "1.0.0", "added", "OAuth support"))
        svc.add_entry(ChangelogEntry("e2", "1.0.0", "fixed", "Rate limit fix"))
        results = svc.search("oauth")
        assert len(results) == 1

    def test_stats(self):
        svc = ChangelogManager()
        svc.add_entry(ChangelogEntry("e1", "1.0.0", "added", "A"))
        svc.add_entry(ChangelogEntry("e2", "1.0.0", "fixed", "B"))
        svc.add_entry(ChangelogEntry("e3", "2.0.0", "removed", "C", breaking=True))
        stats = svc.get_stats()
        assert stats["total_entries"] == 3
        assert stats["versions"] == 2
        assert stats["breaking_changes"] == 1

    def test_invalid_type(self):
        svc = ChangelogManager()
        with pytest.raises(ValueError):
            svc.add_entry(ChangelogEntry("e1", "1.0.0", "unknown", "X"))

    def test_empty_description(self):
        svc = ChangelogManager()
        with pytest.raises(ValueError):
            svc.add_entry(ChangelogEntry("e1", "1.0.0", "added", ""))

    def test_isolation(self):
        a, b = ChangelogManager(), ChangelogManager()
        a.add_entry(ChangelogEntry("e1", "1.0.0", "added", "X"))
        assert b.list_versions() == []
