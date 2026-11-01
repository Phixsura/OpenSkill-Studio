"""Changelog formatter tests."""
from app.services.app_changelog_formatter import format_release_notes, format_full_changelog

def test_format_basic():
    notes = format_release_notes(version="1.0.0", changes=[{"type": "added", "description": "Initial release"}])
    assert "v1.0.0" in notes
    assert "✨" in notes

def test_format_breaking():
    notes = format_release_notes(version="2.0.0", changes=[], breaking=True)
    assert "BREAKING" in notes

def test_format_full():
    releases = [
        {"version": "2.0.0", "changes": [{"type": "added", "description": "New feature"}], "breaking": False},
        {"version": "1.0.0", "changes": [{"type": "fixed", "description": "Bug fix"}]},
    ]
    md = format_full_changelog(releases)
    assert "v2.0.0" in md
    assert "v1.0.0" in md
    assert "🐛" in md

def test_multiple_change_types():
    changes = [
        {"type": "added", "description": "Feature A"},
        {"type": "security", "description": "Fix CVE"},
        {"type": "removed", "description": "Legacy endpoint"},
    ]
    notes = format_release_notes(version="3.0.0", changes=changes)
    assert "✨" in notes and "🔒" in notes and "🗑️" in notes
