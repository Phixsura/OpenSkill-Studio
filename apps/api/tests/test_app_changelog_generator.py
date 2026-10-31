"""Tests for App Changelog Generator — releases, entries, markdown, stats."""

import pytest

from app.services.app_changelog_generator import (
    AppChangelogGenerator,
    ChangeCategory,
)


class TestAddRelease:
    def test_create_release(self):
        g = AppChangelogGenerator()
        r = g.add_release("app-1", "1.0.0", "2026-10-28")
        assert r.version == "1.0.0"
        assert r.date == "2026-10-28"

    def test_duplicate_version(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-10-28")
        with pytest.raises(ValueError, match="already exists"):
            g.add_release("app-1", "1.0.0", "2026-10-29")

    def test_missing_app_id(self):
        g = AppChangelogGenerator()
        with pytest.raises(ValueError, match="app_id"):
            g.add_release("", "1.0.0", "2026-10-28")

    def test_missing_version(self):
        g = AppChangelogGenerator()
        with pytest.raises(ValueError, match="version"):
            g.add_release("app-1", "", "2026-10-28")


class TestAddEntry:
    def test_add_entry(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-10-28")
        e = g.add_entry("app-1", "1.0.0", "New feature", ChangeCategory.ADDED)
        assert e.description == "New feature"
        assert e.category == ChangeCategory.ADDED

    def test_breaking_entry(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "2.0.0", "2026-10-28")
        e = g.add_entry("app-1", "2.0.0", "Removed v1 API", ChangeCategory.REMOVED, breaking=True)
        assert e.breaking is True

    def test_empty_description(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-10-28")
        with pytest.raises(ValueError, match="description"):
            g.add_entry("app-1", "1.0.0", "", ChangeCategory.FIXED)

    def test_unknown_release(self):
        g = AppChangelogGenerator()
        with pytest.raises(KeyError):
            g.add_entry("app-1", "9.9.9", "Fix", ChangeCategory.FIXED)


class TestListReleases:
    def test_semver_ordering(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-01-01")
        g.add_release("app-1", "2.0.0", "2026-06-01")
        g.add_release("app-1", "1.5.0", "2026-03-01")
        releases = g.list_releases("app-1")
        assert [r.version for r in releases] == ["2.0.0", "1.5.0", "1.0.0"]

    def test_limit(self):
        g = AppChangelogGenerator()
        for i in range(5):
            g.add_release("app-1", f"1.{i}.0", "2026-01-01")
        assert len(g.list_releases("app-1", limit=3)) == 3

    def test_empty_app(self):
        g = AppChangelogGenerator()
        assert g.list_releases("app-1") == []


class TestBreakingChanges:
    def test_has_breaking(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "2.0.0", "2026-10-28")
        g.add_entry("app-1", "2.0.0", "Removed API", ChangeCategory.REMOVED, breaking=True)
        assert g.has_breaking_changes("app-1", "2.0.0") is True

    def test_no_breaking(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.1.0", "2026-10-28")
        g.add_entry("app-1", "1.1.0", "Bug fix", ChangeCategory.FIXED)
        assert g.has_breaking_changes("app-1", "1.1.0") is False


class TestRenderMarkdown:
    def test_basic_render(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-10-28", summary="Initial release")
        g.add_entry("app-1", "1.0.0", "Core API", ChangeCategory.ADDED)
        g.add_entry("app-1", "1.0.0", "Startup crash", ChangeCategory.FIXED)
        md = g.render_markdown("app-1")
        assert "# Changelog" in md
        assert "[1.0.0]" in md
        assert "Core API" in md
        assert "Startup crash" in md

    def test_breaking_marker(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "2.0.0", "2026-10-28")
        g.add_entry("app-1", "2.0.0", "Removed v1", ChangeCategory.REMOVED, breaking=True)
        md = g.render_markdown("app-1")
        assert "BREAKING" in md

    def test_empty_changelog(self):
        g = AppChangelogGenerator()
        md = g.render_markdown("app-1")
        assert "No releases yet" in md

    def test_category_sections(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-10-28")
        g.add_entry("app-1", "1.0.0", "Feature A", ChangeCategory.ADDED)
        g.add_entry("app-1", "1.0.0", "Vuln fix", ChangeCategory.SECURITY)
        md = g.render_markdown("app-1")
        assert "### Added" in md
        assert "### Security" in md


class TestStats:
    def test_stats(self):
        g = AppChangelogGenerator()
        g.add_release("app-1", "1.0.0", "2026-10-28")
        g.add_entry("app-1", "1.0.0", "A", ChangeCategory.ADDED)
        g.add_entry("app-1", "1.0.0", "B", ChangeCategory.ADDED)
        g.add_entry("app-1", "1.0.0", "C", ChangeCategory.FIXED)
        stats = g.get_stats("app-1")
        assert stats["added"] == 2
        assert stats["fixed"] == 1
        assert stats["removed"] == 0
