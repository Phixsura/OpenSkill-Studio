from app.services.app_marketplace_app_app_app_app_page_layout import build_page_layout

def test_layout():
    r = build_page_layout(
        page_title="App Settings",
        breadcrumbs=[{"label": "Home", "href": "/"}, {"label": "Settings"}],
        sidebar_items=[{"label": "General", "href": "/settings", "icon": "⚙️", "active": True}],
        user={"name": "Alice Chen"}, notifications=5)
    assert r["page_title"] == "App Settings"
    assert len(r["breadcrumbs"]) == 2
    assert r["user"]["initials"] == "AC"
    assert r["notifications"] == 5
    assert r["has_sidebar"]
