from app.services.app_marketplace_app_breadcrumb_builder import build_breadcrumb, build_marketplace_breadcrumb

def test_basic():
    b = build_breadcrumb(segments=[{"label": "Apps", "url": "/apps"}])
    assert b[0]["label"] == "Home"
    assert b[1]["label"] == "Apps"

def test_app_breadcrumb():
    b = build_marketplace_breadcrumb(page_type="app", context={"app_name": "SuperApp", "app_slug": "super-app", "category_name": "Connectors", "category_id": "connector"})
    labels = [c["label"] for c in b]
    assert "Home" in labels
    assert "Marketplace" in labels
    assert "Connectors" in labels
    assert "SuperApp" in labels

def test_developer_breadcrumb():
    b = build_marketplace_breadcrumb(page_type="developer", context={"developer_name": "DevCo", "developer_slug": "devco"})
    assert b[-1]["label"] == "DevCo"
