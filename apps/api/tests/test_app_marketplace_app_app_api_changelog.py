from app.services.app_marketplace_app_app_api_changelog import list_api_versions, get_api_changelog

def test_list():
    r = list_api_versions()
    assert r["total"] == 2
    assert r["latest"] == "2026-10-01"

def test_get():
    r = get_api_changelog(version="2026-10-01")
    assert r["total"] == 3
    assert r["has_breaking"]  # has "changed"

def test_unknown():
    r = get_api_changelog(version="2020-01-01")
    assert "error" in r
