from app.services.app_marketplace_app_app_app_discovery import recommend_apps

def test_recommend():
    catalog = [
        {"id": "a1", "name": "Code Tool", "tags": ["code", "tools"], "category": "tools", "rating": 4.5},
        {"id": "a2", "name": "Chat App", "tags": ["chat"], "category": "communication", "rating": 4.0},
        {"id": "a3", "name": "Dev IDE", "tags": ["code", "editor"], "category": "tools", "rating": 4.8},
    ]
    r = recommend_apps(user_interests=["code", "tools"], installed_apps=["a1"], catalog=catalog)
    assert r["total_found"] == 1  # a3 (a1 installed, a2 no overlap)
    assert r["recommendations"][0]["name"] == "Dev IDE"

def test_no_matches():
    r = recommend_apps(user_interests=["gaming"], installed_apps=[], catalog=[{"id": "x", "tags": ["finance"], "category": "finance", "rating": 3}])
    assert r["total_found"] == 0
