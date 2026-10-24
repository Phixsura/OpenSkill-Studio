from app.services.app_marketplace_changelog_page_final import build_changelog_page_final

def test_all():
    p = build_changelog_page_final(
        platform_updates=[{"title": "v3.0", "date": "2026-10-20"}],
        app_updates=[{"title": "App v2", "date": "2026-10-22"}],
        api_changes=[{"title": "API v3", "date": "2026-10-21"}])
    assert p["total"] == 3
    assert p["entries"][0]["title"] == "App v2"  # newest first

def test_filter():
    p = build_changelog_page_final(
        platform_updates=[{"title": "P1", "date": "2026-10-01"}],
        app_updates=[{"title": "A1", "date": "2026-10-02"}],
        api_changes=[], filter_type="platform")
    assert p["total"] == 1
    assert p["active_filter"] == "platform"
