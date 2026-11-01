from app.services.app_marketplace_changelog_viewer import get_changelog_page, get_changelog_summary, search_changelog

def test_page():
    entries = [{"version": f"1.{i}", "changes": [{"type": "feat"}]} for i in range(25)]
    r = get_changelog_page(entries=entries, page=2, per_page=10)
    assert len(r["entries"]) == 10
    assert r["total_pages"] == 3
    assert r["has_next"]

def test_filter():
    entries = [{"version": "2.0", "changes": [{"type": "feat"}]},
               {"version": "1.1", "changes": [{"type": "fix"}]}]
    r = get_changelog_page(entries=entries, type_filter="fix")
    assert r["total"] == 1

def test_summary():
    entries = [{"version": "2.0", "changes": [{"type": "feat"}, {"type": "fix"}], "has_breaking": True},
               {"version": "1.0", "changes": [{"type": "feat"}]}]
    s = get_changelog_summary(entries=entries)
    assert s["total_changes"] == 3
    assert s["breaking_versions"] == 1
    assert s["latest"] == "2.0"

def test_search():
    entries = [{"version": "2.0", "changes": [{"description": "Add dark mode"}, {"description": "Fix bug"}]}]
    r = search_changelog(entries=entries, query="dark")
    assert len(r) == 1
    assert r[0]["version"] == "2.0"
