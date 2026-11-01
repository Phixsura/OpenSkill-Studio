from app.services.app_marketplace_app_app_app_detail_header import build_app_detail_header

def test_header():
    app = {"name": "Auth SDK", "developer": "Alice Dev", "tagline": "Easy authentication",
           "avg_rating": 4.7, "review_count": 120, "install_count": 8500,
           "price": 0, "category": "security", "verified_developer": True, "version": "2.1.0"}
    r = build_app_detail_header(app=app)
    assert r["name"] == "Auth SDK"
    assert r["developer"] == "Alice Dev"
    assert r["install_display"] == "8K+"
    assert r["price_label"] == "Free"
    assert r["verified"]
    assert r["stars"] == "★★★★★"

def test_paid():
    r = build_app_detail_header(app={"name": "Pro Tool", "price": 29.99, "install_count": 500})
    assert r["price_label"] == "$29.99/mo"
    assert r["install_display"] == "500"

def test_xss():
    r = build_app_detail_header(app={"name": "<script>xss</script>"})
    assert "<script>" not in r["name"]
