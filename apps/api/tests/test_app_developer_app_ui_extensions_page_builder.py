from app.services.app_developer_app_ui_extensions_page_builder import build_extensions_page

def test_page():
    p = build_extensions_page(extensions=[{"surface": "dashboard_card", "title": "Card"}],
        surfaces_available=["dashboard_card", "project_sidebar", "settings_tab"])
    assert p["count"] == 1
    assert "project_sidebar" in p["unused_surfaces"]
