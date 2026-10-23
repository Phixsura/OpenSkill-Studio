from app.services.app_marketplace_app_app_app_app_app_app_app_breadcrumb_nav import build_breadcrumbs, get_parent_path

def test_breadcrumbs():
    crumbs = build_breadcrumbs("/apps/my-app/settings")
    assert len(crumbs) == 4
    assert crumbs[0]["label"] == "Home"
    assert crumbs[1]["label"] == "Apps"
    assert crumbs[2]["label"] == "My App"
    assert crumbs[3]["label"] == "Settings"
    assert crumbs[3]["active"]
    assert not crumbs[0]["active"]

def test_parent():
    assert get_parent_path("/apps/my-app/settings") == "/apps/my-app"
    assert get_parent_path("/apps") == "/"
    assert get_parent_path("/") == "/"
