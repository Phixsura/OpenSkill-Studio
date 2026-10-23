from app.services.app_marketplace_app_app_navigation_menu import build_navigation

def test_viewer():
    r = build_navigation(user_role="viewer", active_path="/marketplace")
    assert r["total"] == 4  # Home, Marketplace, Settings, Docs
    assert not any(i["path"] == "/apps" for i in r["items"])
    active = next(i for i in r["items"] if i["active"])
    assert active["path"] == "/marketplace"

def test_developer():
    r = build_navigation(user_role="developer")
    assert any(i["path"] == "/apps" for i in r["items"])
    assert not any(i["path"] == "/admin" for i in r["items"])

def test_admin():
    r = build_navigation(user_role="admin")
    assert r["total"] == 8
    assert any(i["path"] == "/admin" for i in r["items"])
