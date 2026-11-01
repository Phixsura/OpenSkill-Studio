from app.services.app_marketplace_app_app_app_badge_system import evaluate_badges

def test_badges():
    app = {"verified": True, "rating": 4.8, "installs": 25000, "open_source": True, "staff_pick": False}
    r = evaluate_badges(app=app)
    assert r["count"] == 4
    assert "verified" in r["badge_ids"]
    assert "top_rated" in r["badge_ids"]
    assert "popular" in r["badge_ids"]
    assert "open_source" in r["badge_ids"]

def test_no_badges():
    r = evaluate_badges(app={"rating": 3.0, "installs": 100})
    assert r["count"] == 0
