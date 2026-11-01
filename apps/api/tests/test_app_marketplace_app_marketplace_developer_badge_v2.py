from app.services.app_marketplace_app_marketplace_developer_badge_v2 import generate_installs_badge, generate_rating_badge, generate_all_badges

def test_installs():
    b = generate_installs_badge(count=5000, app_slug="my-app")
    assert b["color"] == "brightgreen"
    assert "5,000" in b["label"]

def test_rating():
    b = generate_rating_badge(rating=4.8, app_slug="my-app")
    assert b["color"] == "brightgreen"
    assert "4.8★" in b["label"]

def test_all():
    app = {"slug": "app", "status": "published", "install_count": 500, "avg_rating": 4.2}
    badges = generate_all_badges(app=app)
    assert len(badges) == 3
    assert badges[0]["type"] == "status"
