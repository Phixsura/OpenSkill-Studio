from app.services.app_marketplace_app_app_app_app_settings_page_complete import build_settings_page_complete

def test_settings():
    r = build_settings_page_complete(app={"id": "a1", "name": "SuperApp", "version": "2.0.0"},
                                      active_tab="security")
    assert r["app_name"] == "SuperApp"
    assert r["tab_count"] == 8
    assert r["active_tab"] == "security"
    security_tab = next(t for t in r["tabs"] if t["id"] == "security")
    assert security_tab["active"]
