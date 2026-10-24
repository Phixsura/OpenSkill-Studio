from app.services.app_marketplace_developer_api_changelog_page import build_api_changelog_page

def test_page():
    versions = [
        {"version": "v3", "date": "2026-10", "endpoints_added": ["/new"], "endpoints_removed": ["/old"], "endpoints_modified": []},
        {"version": "v2", "date": "2026-06", "endpoints_added": ["/users"], "endpoints_removed": [], "endpoints_modified": ["/apps"]},
    ]
    p = build_api_changelog_page(versions=versions)
    assert p["total_versions"] == 2
    assert p["breaking_releases"] == 1
    assert p["latest"] == "v3"
    assert p["stability_score"] == 85.0

def test_empty():
    p = build_api_changelog_page(versions=[])
    assert p["latest"] is None
    assert p["stability_score"] == 100
