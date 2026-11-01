from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_diff import parse_changelog, diff_changelogs

def test_parse():
    entries = [
        {"type": "feat", "description": "New dashboard", "breaking": False},
        {"type": "fix", "description": "Login bug", "breaking": False},
        {"type": "feat", "description": "API v2", "breaking": True},
    ]
    r = parse_changelog(entries)
    assert r["total"] == 3
    assert r["breaking_count"] == 1
    assert r["by_type"]["feat"] == ["New dashboard", "API v2"]

def test_diff():
    old = [{"description": "A"}, {"description": "B"}]
    new = [{"description": "B"}, {"description": "C"}, {"description": "D"}]
    r = diff_changelogs(old, new)
    assert r["added_count"] == 2
    assert r["removed_count"] == 1
    assert r["net_change"] == 1
