from app.services.app_marketplace_app_app_app_app_app_app_app_app_reviews import AppReviewSystem

def test_reviews():
    rs = AppReviewSystem()
    rs.submit(app_id="app1", user_id="u1", rating=5, title="Amazing", body="Love it")
    rs.submit(app_id="app1", user_id="u2", rating=4, title="Good")
    rs.submit(app_id="app1", user_id="u3", rating=3, title="OK")
    reviews = rs.get_reviews("app1")
    assert len(reviews) == 3
    s = rs.summary("app1")
    assert s["count"] == 3
    assert s["avg_rating"] == 4.0
    assert s["distribution"][5] == 1
    assert s["distribution"][4] == 1
