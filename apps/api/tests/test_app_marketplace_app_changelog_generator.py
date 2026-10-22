from app.services.app_marketplace_app_changelog_generator import generate_changelog_entry, render_changelog_markdown, compare_versions_for_changelog

def test_entry():
    e = generate_changelog_entry(version="2.0.0", changes=[
        {"type": "added", "description": "Dark mode"},
        {"type": "fixed", "description": "Login bug"},
    ])
    assert e["total_changes"] == 2
    assert "Dark mode" in e["categories"]["added"]

def test_markdown():
    entries = [generate_changelog_entry(version="1.0", changes=[{"type": "added", "description": "Initial"}])]
    md = render_changelog_markdown(entries=entries)
    assert "# Changelog" in md
    assert "## 1.0" in md

def test_compare():
    changes = compare_versions_for_changelog(
        old_manifest={"permissions": ["read"], "entry_point": "old.js"},
        new_manifest={"permissions": ["read", "write"], "entry_point": "new.js"})
    assert any("write" in c["description"] for c in changes)
    assert any("Entry point" in c["description"] for c in changes)
