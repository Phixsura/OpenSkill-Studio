from app.services.app_marketplace_app_app_feedback_form import analyze_feedback, build_feedback_summary

def test_positive():
    r = analyze_feedback(text="This app is amazing and fast!", rating=5)
    assert r["sentiment"] == "positive"
    assert "amazing" in r["positive_signals"]

def test_negative():
    r = analyze_feedback(text="Terrible app, keeps crashing", rating=1)
    assert r["sentiment"] == "negative"

def test_neutral():
    r = analyze_feedback(text="It works okay", rating=3)
    assert r["sentiment"] == "neutral"

def test_summary():
    feedbacks = [
        {"text": "Great!", "rating": 5},
        {"text": "Bad", "rating": 1},
        {"text": "OK", "rating": 3},
    ]
    r = build_feedback_summary(feedbacks=feedbacks)
    assert r["total"] == 3
    assert r["avg_rating"] == 3.0
