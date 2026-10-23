from app.services.app_marketplace_complete_app_changelog_page import build_complete_changelog_page

def test_page():
    versions = [{"version": "2.0", "released_at": "2026-06-01", "changes": [{"type": "feat"}], "has_breaking": True},
                {"version": "1.0", "released_at": "2026-01-01", "changes": [{"type": "feat"}, {"type": "fix"}]}]
    p = build_complete_changelog_page(app={"id": "a1", "name": "App", "slug": "app"}, versions=versions)
    assert p["stats"]["total_versions"] == 2
    assert p["stats"]["total_changes"] == 3
    assert p["stats"]["breaking_releases"] == 1
    assert p["latest_version"] == "2.0"
    assert ".rss" in p["rss_url"]
