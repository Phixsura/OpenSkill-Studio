"""App changelog service tests."""

import pytest
from app.services.app_changelog import generate_changelog_entry, format_changelog_markdown

V1 = {"permissions": ["read:cohorts"], "event_subscriptions": ["submission.completed"]}
V2 = {"permissions": ["read:cohorts", "write:cohorts"], "event_subscriptions": ["submission.completed", "cohort.member_added"],
      "secrets": [{"key": "NEW_KEY"}]}

def test_entry_basic():
    e = generate_changelog_entry(version="2.0.0", old_manifest=V1, new_manifest=V2)
    assert e["version"] == "2.0.0"
    assert not e["breaking"]
    assert len(e["changes"]) > 0

def test_entry_breaking():
    e = generate_changelog_entry(version="1.0.0", old_manifest=V2, new_manifest=V1)
    assert e["breaking"] is True

def test_entry_with_notes():
    e = generate_changelog_entry(version="2.0.0", old_manifest=V1, new_manifest=V2, changelog_text="Added write support")
    assert e["notes"] == "Added write support"

def test_entry_first_version():
    e = generate_changelog_entry(version="1.0.0", old_manifest=None, new_manifest=V1)
    assert e["version"] == "1.0.0"
    assert e["changes"] == []

def test_entry_permissions_change():
    e = generate_changelog_entry(version="2.0.0", old_manifest=V1, new_manifest=V2)
    types = [c["type"] for c in e["changes"]]
    assert "permissions_added" in types

def test_entry_events_change():
    e = generate_changelog_entry(version="2.0.0", old_manifest=V1, new_manifest=V2)
    types = [c["type"] for c in e["changes"]]
    assert "events_added" in types

def test_format_markdown():
    entries = [
        generate_changelog_entry(version="2.0.0", old_manifest=V1, new_manifest=V2, changelog_text="Big update"),
        generate_changelog_entry(version="1.0.0", old_manifest=None, new_manifest=V1, changelog_text="Initial release"),
    ]
    md = format_changelog_markdown(entries)
    assert "# Changelog" in md
    assert "## 2.0.0" in md
    assert "## 1.0.0" in md
    assert "Big update" in md

def test_format_breaking_marker():
    entries = [generate_changelog_entry(version="1.0.0", old_manifest=V2, new_manifest=V1)]
    md = format_changelog_markdown(entries)
    assert "BREAKING" in md

def test_format_empty():
    md = format_changelog_markdown([])
    assert "# Changelog" in md
