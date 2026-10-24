from app.services.app_marketplace_app_app_listing_preview import generate_listing_preview

def test_preview():
    app = {"name": "Auth SDK", "description": "A fantastic authentication SDK for developers " * 3,
           "developer_name": "Alice", "avg_rating": 4.7, "install_count": 5000,
           "price": 0, "icon_url": "icon.png", "category": "security", "version": "2.0",
           "screenshots": ["s1.png", "s2.png"]}
    r = generate_listing_preview(app=app)
    assert r["card"]["name"] == "Auth SDK"
    assert r["card"]["price_label"] == "Free"
    assert r["card"]["rating"] == 4.7
    assert r["detail"]["screenshot_count"] == 2
    assert r["completeness"]["pct"] == 100

def test_xss():
    app = {"name": "<script>alert(1)</script>", "description": "ok"}
    r = generate_listing_preview(app=app)
    assert "<script>" not in r["card"]["name"]

def test_incomplete():
    r = generate_listing_preview(app={"name": "App"})
    assert r["completeness"]["pct"] < 50
