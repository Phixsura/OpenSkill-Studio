from app.services.app_marketplace_app_app_app_app_app_app_app_nav_helper import get_nav_for_role, get_active_section, build_nav

def test_role_nav():
    admin_nav = get_nav_for_role("admin")
    assert len(admin_nav) == 8
    viewer_nav = get_nav_for_role("viewer")
    assert len(viewer_nav) == 3  # overview, apps, docs

def test_active():
    assert get_active_section("/apps/my-app") == "apps"
    assert get_active_section("/") == "overview"
    assert get_active_section("/billing") == "billing"

def test_build():
    r = build_nav(role="admin", active_path="/apps", badges={"webhooks": 3})
    assert r["active"] == "apps"
    wh = next(i for i in r["items"] if i["id"] == "webhooks")
    assert wh["badge"] == 3
