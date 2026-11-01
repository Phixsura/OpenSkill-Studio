from app.services.app_marketplace_app_app_app_app_app_app_app_sidebar_nav import build_sidebar, get_nav_item

def test_sidebar():
    r = build_sidebar(active="apps", badges={"webhooks": 3, "team": 1})
    assert r["total_items"] == 10
    apps_item = next(i for i in r["items"] if i["id"] == "apps")
    assert apps_item["active"]
    wh = next(i for i in r["items"] if i["id"] == "webhooks")
    assert wh["badge"] == 3

def test_get_item():
    item = get_nav_item("dashboard")
    assert item["label"] == "Dashboard"
    assert get_nav_item("nonexistent") is None
