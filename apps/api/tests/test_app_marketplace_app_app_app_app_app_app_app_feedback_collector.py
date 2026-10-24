from app.services.app_marketplace_app_app_app_app_app_app_app_feedback_collector import FeedbackCollector

def test_feedback():
    fc = FeedbackCollector()
    fc.submit(user_id="u1", category="ui", rating=5, message="Love it!")
    fc.submit(user_id="u2", category="ui", rating=4, message="Great")
    fc.submit(user_id="u3", category="api", rating=2, message="Slow")
    fc.submit(user_id="u4", category="docs", rating=1, message="Missing")
    s = fc.summary()
    assert s["total"] == 4
    assert s["avg_rating"] == 3.0
    assert s["by_category"]["ui"]["count"] == 2
    assert s["promoters"] == 2
    assert s["detractors"] == 2
    assert s["nps"] == 0
