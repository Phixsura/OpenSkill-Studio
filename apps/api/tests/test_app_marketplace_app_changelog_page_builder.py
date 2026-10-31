from app.services.app_marketplace_app_changelog_page_builder import build_changelog_page

def test_page():
    p = build_changelog_page(app_name="X", versions=[{"version": "2.0"}, {"version": "1.0"}])
    assert p["version_count"] == 2
