from app.services.app_marketplace_app_app_marketplace_search import search_marketplace

def test_search():
    apps = [
        {"id": "a1", "name": "Auth SDK", "description": "Authentication", "category": "security", "rating": 4.5, "price": 0},
        {"id": "a2", "name": "Chart Builder", "description": "Beautiful charts", "category": "design", "rating": 4.0, "price": 9.99},
        {"id": "a3", "name": "Auth Helper", "description": "Auth utilities", "category": "security", "rating": 3.8, "price": 0},
    ]
    r = search_marketplace(query="auth", apps=apps)
    assert r["total"] == 2
    assert r["results"][0]["name"] == "Auth SDK"  # higher score (starts with + contains)

def test_filter():
    apps = [
        {"id": "a1", "name": "Free Auth", "category": "security", "rating": 4.5, "price": 0},
        {"id": "a2", "name": "Paid Auth", "category": "security", "rating": 4.0, "price": 10},
    ]
    r = search_marketplace(query="auth", apps=apps, filters={"free_only": True})
    assert r["total"] == 1

def test_no_results():
    r = search_marketplace(query="zzz", apps=[{"name": "Auth"}])
    assert r["total"] == 0
