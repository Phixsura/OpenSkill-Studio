from app.services.app_marketplace_app_developer_changelog_v3 import build_interactive_changelog, filter_changelog

def test_build():
    versions = [
        {"version": "2.0", "released_at": "2026-06-01", "changes": [{"type": "feat", "breaking": True}]},
        {"version": "1.0", "released_at": "2026-01-01", "changes": [{"type": "feat"}]},
    ]
    c = build_interactive_changelog(versions=versions)
    assert c["latest"] == "2.0"
    assert c["entries"][0]["previous_version"] == "1.0"
    assert c["entries"][0]["has_breaking"]

def test_filter_breaking():
    entries = [{"has_breaking": True, "changes": []}, {"has_breaking": False, "changes": []}]
    r = filter_changelog(entries=entries, breaking_only=True)
    assert len(r) == 1
