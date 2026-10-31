from app.services.app_marketplace_app_app_score_card import calculate_app_score

def test_high_score():
    app = {"description": "x" * 50, "screenshot_count": 5, "has_docs": True,
           "has_tests": True, "avg_rating": 4.8, "install_count": 5000,
           "updated_recently": True, "has_support_email": True}
    r = calculate_app_score(app=app)
    assert r["grade"] in ("A+", "A")
    assert r["score"] >= 80

def test_low_score():
    r = calculate_app_score(app={"description": "Hi"})
    assert r["grade"] in ("D", "F")
    assert len(r["improvements"]) > 3

def test_criteria():
    app = {"description": "A decent description for testing", "screenshot_count": 2}
    r = calculate_app_score(app=app)
    assert "description_quality" in r["criteria"]
    assert "screenshots" in r["criteria"]
