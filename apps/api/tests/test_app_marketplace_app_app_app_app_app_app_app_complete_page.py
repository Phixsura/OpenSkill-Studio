from app.services.app_marketplace_app_app_app_app_app_app_app_complete_page import build_complete_page

def test_page():
    r = build_complete_page(title="App Settings", sections=[
        {"id": "general", "title": "General", "type": "form"},
        {"id": "permissions", "title": "Permissions", "type": "table"},
        {"id": "danger", "title": "Danger Zone", "type": "danger", "collapsed": True},
    ], sidebar={"nav": ["general", "permissions"]})
    assert r["title"] == "App Settings"
    assert r["section_count"] == 3
    assert r["has_sidebar"]
    assert r["sections"][2]["collapsed"]
