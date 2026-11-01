from app.services.app_breadcrumb_builder import build_breadcrumbs

def test_developer():
    bc = build_breadcrumbs("developer")
    assert bc[-1]["label"] == "Developer"

def test_apps():
    bc = build_breadcrumbs("apps")
    assert len(bc) == 3

def test_marketplace_app():
    bc = build_breadcrumbs("marketplace_app", slug="my-app", name="My App")
    assert bc[-1]["label"] == "My App"

def test_unknown():
    assert build_breadcrumbs("nonexist") == []
