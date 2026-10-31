from app.services.app_marketplace_app_card_builder import build_app_card

def test_basic():
    c = build_app_card(app={"id": "a1", "name": "App", "slug": "app", "category": "connector", "status": "published"},
        developer={"display_name": "Dev", "verified": True}, install_count=42, health_score=95)
    assert c["name"] == "App"
    assert c["developer"]["verified"] is True
    assert c["install_count"] == 42

def test_no_developer():
    c = build_app_card(app={"id": "a", "name": "X"})
    assert c["developer"]["name"] is None

def test_with_badges():
    c = build_app_card(app={"id": "a"}, badges=[{"label": "Popular"}])
    assert len(c["badges"]) == 1
