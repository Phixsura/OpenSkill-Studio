from app.services.app_marketplace_breadcrumb_v2 import build_smart_breadcrumb, get_structured_breadcrumb

def test_breadcrumb():
    b = build_smart_breadcrumb(path_segments=["marketplace", "apps", "super-app"],
                                 labels={"marketplace": "Marketplace", "apps": "Apps", "super-app": "SuperApp"},
                                 current_page="super-app")
    assert b[0]["label"] == "Home"
    assert b[-1]["label"] == "SuperApp"
    assert b[-1]["active"]
    assert b[-1]["url"] is None  # active page has no link

def test_structured():
    crumbs = [{"label": "Home", "url": "/"}, {"label": "Apps", "url": "/apps"}]
    s = get_structured_breadcrumb(crumbs=crumbs)
    assert s["@type"] == "BreadcrumbList"
    assert len(s["itemListElement"]) == 2
    assert s["itemListElement"][0]["position"] == 1
