"""Tests for App Changelog AI Summary — headline, bullets, breaking."""

import pytest

from app.services.app_changelog_ai_summary import AppChangelogAISummary, SummaryEntry


class TestSummarize:
    def test_basic(self):
        s = AppChangelogAISummary()
        entries = [
            SummaryEntry(title="New API endpoint", category="added"),
            SummaryEntry(title="Fixed login bug", category="fixed"),
        ]
        result = s.summarize("2.0.0", entries)
        assert result.version == "2.0.0"
        assert result.total_changes == 2
        assert "2 changes" in result.headline

    def test_breaking_in_headline(self):
        s = AppChangelogAISummary()
        entries = [
            SummaryEntry(title="Removed v1 API", category="removed", breaking=True),
            SummaryEntry(title="New endpoint", category="added"),
        ]
        result = s.summarize("3.0.0", entries)
        assert "breaking" in result.headline.lower()
        assert result.breaking_count == 1

    def test_breaking_first_in_bullets(self):
        s = AppChangelogAISummary()
        entries = [
            SummaryEntry(title="Feature A", category="added"),
            SummaryEntry(title="Removed old API", category="removed", breaking=True),
        ]
        result = s.summarize("2.0.0", entries)
        assert result.bullet_points[0].startswith("⚠")

    def test_category_counts(self):
        s = AppChangelogAISummary()
        entries = [
            SummaryEntry(title="A", category="added"),
            SummaryEntry(title="B", category="added"),
            SummaryEntry(title="C", category="fixed"),
        ]
        result = s.summarize("1.0.0", entries)
        assert result.category_counts["added"] == 2
        assert result.category_counts["fixed"] == 1

    def test_grouped_bullets(self):
        s = AppChangelogAISummary()
        entries = [
            SummaryEntry(title="Feature A", category="added"),
            SummaryEntry(title="Feature B", category="added"),
            SummaryEntry(title="Bug fix", category="fixed"),
        ]
        result = s.summarize("1.0.0", entries)
        # Should mention "+1 more added"
        assert any("+1 more" in b for b in result.bullet_points)

    def test_empty_entries(self):
        s = AppChangelogAISummary()
        with pytest.raises(ValueError, match="at least one"):
            s.summarize("1.0.0", [])

    def test_missing_version(self):
        s = AppChangelogAISummary()
        with pytest.raises(ValueError, match="version"):
            s.summarize("", [SummaryEntry(title="X", category="added")])

    def test_bullet_cap(self):
        s = AppChangelogAISummary()
        entries = [SummaryEntry(title=f"Change {i}", category=f"cat{i}") for i in range(20)]
        result = s.summarize("1.0.0", entries)
        assert len(result.bullet_points) <= 10
