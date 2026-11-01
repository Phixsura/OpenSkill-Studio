from app.services.app_marketplace_app_app_changelog_entry import create_entry, group_entries

def test_create():
    r = create_entry(type="added", title="Dark mode", description="New theme option", pr_number=42, author="Alice")
    assert r["icon"] == "✨"
    assert r["title"] == "Dark mode"
    assert r["pr_number"] == 42

def test_group():
    entries = [
        {"type": "added", "title": "Feature A"},
        {"type": "fixed", "title": "Bug B"},
        {"type": "added", "title": "Feature C"},
    ]
    r = group_entries(entries=entries)
    assert r["total"] == 3
    assert r["groups"][0]["type"] == "added"
    assert r["groups"][0]["count"] == 2
