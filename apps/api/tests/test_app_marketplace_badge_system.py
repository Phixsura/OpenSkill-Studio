from app.services.app_marketplace_badge_system import compute_badges, get_badge_info

def test_badges():
    app = {"developer_verified": True, "install_count": 5000, "avg_rating": 4.8,
           "review_count": 50, "trending": True}
    b = compute_badges(app=app)
    labels = [x["label"] for x in b]
    assert "Verified" in labels
    assert "Popular" in labels
    assert "Top Rated" in labels
    assert "Trending" in labels

def test_no_badges():
    b = compute_badges(app={"install_count": 5})
    assert len(b) == 0

def test_badge_info():
    b = get_badge_info(badge_id="popular")
    assert b["icon"] == "🔥"

def test_unknown_badge():
    assert get_badge_info(badge_id="nonexistent") is None
