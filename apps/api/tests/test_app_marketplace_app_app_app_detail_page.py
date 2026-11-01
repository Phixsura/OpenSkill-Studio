from app.services.app_marketplace_app_app_app_detail_page import build_app_detail_page

def test_detail():
    app = {"name": "Auth SDK", "developer": "Alice", "tagline": "Easy auth",
           "avg_rating": 4.7, "install_count": 8500, "price": 0, "version": "2.1",
           "description": "Authentication made easy", "screenshots": ["s1.png"],
           "permissions": ["read"], "changelog": [{"version": "2.1"}]}
    reviews = [{"rating": 5, "text": "Great!"}, {"rating": 4, "text": "Good"}]
    related = [{"id": "a2", "name": "OAuth Kit"}]
    r = build_app_detail_page(app=app, reviews=reviews, related_apps=related)
    assert r["header"]["name"] == "Auth SDK"
    assert r["reviews"]["total"] == 2
    assert r["reviews"]["avg_rating"] == 4.5
    assert len(r["related_apps"]) == 1
    assert len(r["tabs"]) == 4

def test_xss():
    app = {"name": "<script>", "developer": "x", "tagline": "y", "description": "z"}
    r = build_app_detail_page(app=app, reviews=[], related_apps=[])
    assert "<script>" not in r["header"]["name"]
