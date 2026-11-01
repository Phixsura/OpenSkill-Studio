from app.services.app_marketplace_app_changelog_diff import diff_versions, summarize_diff

def test_diff():
    old = {"name": "App", "version": "1.0", "description": "Old desc", "category": "tools"}
    new = {"name": "App", "version": "2.0", "description": "New desc", "icon": "new.png"}
    r = diff_versions(old_version=old, new_version=new)
    assert "icon" in r["added_fields"]
    assert "category" in r["removed_fields"]
    assert r["total_changes"] == 4  # 1 added + 1 removed + 2 modified
    assert r["has_breaking"]  # removed field

def test_no_changes():
    v = {"name": "App", "version": "1.0"}
    r = diff_versions(old_version=v, new_version=v)
    assert r["total_changes"] == 0

def test_summarize():
    diff = {"added_fields": ["icon"], "removed_fields": [], "modified_fields": [{"field": "version"}]}
    assert "Added: icon" in summarize_diff(diff=diff)
    assert "Modified: version" in summarize_diff(diff=diff)
