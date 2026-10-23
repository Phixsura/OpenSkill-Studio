from app.services.app_marketplace_app_app_app_app_app_app_app_complete_nav import build_complete_nav

def test_nav():
    r = build_complete_nav(active_section="marketplace", active_console="dashboard")
    assert r["main_count"] == 5
    assert r["console_count"] == 8
    assert r["main_nav"][0]["active"]
    assert r["console_nav"][0]["active"]
    assert "Product" in r["footer_nav"]
    assert len(r["footer_nav"]) == 4
