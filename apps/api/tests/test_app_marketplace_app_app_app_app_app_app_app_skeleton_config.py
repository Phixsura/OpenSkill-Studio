from app.services.app_marketplace_app_app_app_app_app_app_app_skeleton_config import get_skeleton, list_pages

def test_skeleton():
    r = get_skeleton("dashboard")
    assert r["page"] == "dashboard"
    assert len(r["blocks"]) == 3
    assert r["blocks"][2]["type"] == "table"

def test_fallback():
    r = get_skeleton("unknown_page")
    assert len(r["blocks"]) == 2

def test_pages():
    p = list_pages()
    assert "dashboard" in p
    assert len(p) == 3
