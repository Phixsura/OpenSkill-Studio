from app.services.app_marketplace_changelog_widget import build_changelog_widget, get_latest_changes

def test_widget():
    versions = [{"version": "2.0", "released_at": "2026-06-01", "changes": [{"type": "feat", "description": "Dark mode"}]},
                {"version": "1.0", "released_at": "2026-01-01", "changes": [{"type": "feat", "description": "Initial"}]}]
    w = build_changelog_widget(app_name="App", versions=versions)
    assert w["showing"] == 2
    assert not w["has_more"]

def test_has_more():
    versions = [{"version": f"{i}.0", "changes": []} for i in range(10)]
    w = build_changelog_widget(app_name="App", versions=versions, max_entries=3)
    assert w["has_more"]

def test_latest():
    versions = [{"version": "2.0", "released_at": "2026-06-01", "changes": [{"description": "New"}]},
                {"version": "1.0", "released_at": "2026-01-01", "changes": [{"description": "Old"}]}]
    r = get_latest_changes(versions=versions, limit=1)
    assert len(r) == 1
    assert r[0]["version"] == "2.0"
