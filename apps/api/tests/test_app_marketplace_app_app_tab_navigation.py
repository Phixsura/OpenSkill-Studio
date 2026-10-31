from app.services.app_marketplace_app_app_tab_navigation import build_tab_config

def test_viewer():
    r = build_tab_config(app_id="a1")
    assert r["total"] == 5
    assert r["default_tab"] == "overview"
    assert not any(t["id"] == "analytics" for t in r["tabs"])

def test_developer():
    r = build_tab_config(app_id="a1", is_developer=True)
    assert any(t["id"] == "analytics" for t in r["tabs"])
    assert any(t["id"] == "settings" for t in r["tabs"])
    assert r["total"] == 7

def test_no_docs():
    r = build_tab_config(app_id="a1", has_docs=False)
    assert not any(t["id"] == "docs" for t in r["tabs"])
