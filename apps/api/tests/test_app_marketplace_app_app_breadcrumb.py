from app.services.app_marketplace_app_app_breadcrumb import build_breadcrumb

def test_breadcrumb():
    items = [
        {"label": "Home", "href": "/"},
        {"label": "Marketplace", "href": "/marketplace"},
        {"label": "My App"},
    ]
    r = build_breadcrumb(items=items)
    assert r["depth"] == 3
    assert r["trail"][0]["href"] == "/"
    assert r["trail"][2]["is_current"]
    assert r["trail"][2]["href"] is None

def test_xss():
    r = build_breadcrumb(items=[{"label": "<script>alert(1)</script>"}])
    assert "<script>" not in r["trail"][0]["label"]
    assert "&lt;" in r["trail"][0]["label"]
