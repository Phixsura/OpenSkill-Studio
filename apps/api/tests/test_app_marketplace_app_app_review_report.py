from app.services.app_marketplace_app_app_review_report import generate_review_report

def test_report():
    reviews = [
        {"rating": 5, "text": "Amazing app!", "responded": True},
        {"rating": 4, "text": "Good overall.", "responded": True},
        {"rating": 2, "text": "Needs work.", "responded": False},
        {"rating": 1, "text": "Crashes often.", "responded": False},
    ]
    r = generate_review_report(app_name="Auth SDK", period="Oct 2026", reviews=reviews)
    assert r["total"] == 4
    assert r["avg_rating"] == 3.0
    assert r["five_star_count"] == 1
    assert r["response_rate"] == 50.0
    assert len(r["highlights"]) == 2
    assert len(r["concerns"]) == 2

def test_empty():
    r = generate_review_report(app_name="X", period="Oct", reviews=[])
    assert r["total"] == 0
