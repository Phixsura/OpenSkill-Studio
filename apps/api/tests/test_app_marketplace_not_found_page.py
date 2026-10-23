from app.services.app_marketplace_not_found_page import build_not_found_page

def test_app():
    p = build_not_found_page(resource_type="app")
    assert p["status_code"] == 404
    assert p["title"] == "App Not Found"
    assert len(p["suggestions"]) == 3

def test_developer():
    p = build_not_found_page(resource_type="developer")
    assert "developer" in p["message"].lower()

def test_generic():
    p = build_not_found_page(resource_type="unknown")
    assert p["title"] == "Page Not Found"
