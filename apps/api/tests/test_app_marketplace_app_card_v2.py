from app.services.app_marketplace_app_card_v2 import build_app_card_v2, build_app_card_list

def test_card():
    c = build_app_card_v2(
        app={"id": "a1", "name": "SuperApp", "slug": "super-app", "description": "A great app", "category": "connector"},
        developer={"display_name": "DevCo", "verified": True},
        stats={"avg_rating": 4.5, "review_count": 50, "installs": 2000})
    assert c["name"] == "SuperApp"
    assert c["rating"] == 4.5
    assert any(b["type"] == "verified" for b in c["badges"])
    assert any(b["type"] == "popular" for b in c["badges"])

def test_list():
    data = [{"app": {"id": "a1", "name": "App"}, "developer": {"display_name": "D"}, "stats": {"avg_rating": 4}}]
    r = build_app_card_list(apps_data=data)
    assert len(r) == 1
    assert r[0]["name"] == "App"
