from app.services.app_marketplace_smart_recommendation import recommend_apps

def test_recommend():
    catalog = [
        {"id": "a1", "name": "Installed", "category": "tools", "rating": 4.0, "install_count": 500},
        {"id": "a2", "name": "Similar", "category": "tools", "rating": 4.5, "install_count": 300},
        {"id": "a3", "name": "Other", "category": "design", "rating": 3.5, "install_count": 100},
    ]
    r = recommend_apps(user_id="u1", installed_apps=["a1"], catalog=catalog, limit=2)
    assert len(r["recommendations"]) == 2
    assert r["total_candidates"] == 2
    # "Similar" (same category) should rank higher
    assert r["recommendations"][0]["id"] == "a2"
    assert r["recommendations"][0]["reason"] == "category_match"

def test_empty():
    r = recommend_apps(user_id="u1", installed_apps=[], catalog=[], limit=5)
    assert len(r["recommendations"]) == 0
