"""Tests for App Changelog Export — markdown, JSON, CSV."""

import json

import pytest

from app.services.app_changelog_export import AppChangelogExport, ExportEntry


@pytest.fixture
def exporter():
    e = AppChangelogExport()
    e.add_entry("inst-1", ExportEntry("2.0.0", "2026-10-28", "New API", "added", True))
    e.add_entry("inst-1", ExportEntry("2.0.0", "2026-10-28", "Bug fix", "fixed"))
    e.add_entry("inst-1", ExportEntry("1.0.0", "2026-01-01", "Initial", "added"))
    return e


class TestMarkdown:
    def test_export(self, exporter):
        r = exporter.export_markdown("inst-1")
        assert r.format == "markdown"
        assert "# Changelog" in r.content
        assert "[2.0.0]" in r.content
        assert "BREAKING" in r.content
        assert r.entry_count == 3

    def test_empty(self):
        e = AppChangelogExport()
        r = e.export_markdown("inst-1")
        assert r.entry_count == 0


class TestJSON:
    def test_export(self, exporter):
        r = exporter.export_json("inst-1")
        assert r.format == "json"
        data = json.loads(r.content)
        assert len(data) == 3
        assert data[0]["version"] == "2.0.0"

    def test_valid_json(self, exporter):
        r = exporter.export_json("inst-1")
        parsed = json.loads(r.content)
        assert isinstance(parsed, list)


class TestCSV:
    def test_export(self, exporter):
        r = exporter.export_csv("inst-1")
        assert r.format == "csv"
        lines = r.content.strip().splitlines()
        assert lines[0] == "version,date,title,category,breaking"
        assert len(lines) == 4  # header + 3 entries

    def test_entry_count(self, exporter):
        r = exporter.export_csv("inst-1")
        assert r.entry_count == 3


class TestIsolation:
    def test_cross_installation(self, exporter):
        r = exporter.export_json("inst-2")
        assert r.entry_count == 0
