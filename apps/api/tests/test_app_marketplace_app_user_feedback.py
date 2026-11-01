from app.services.app_marketplace_app_user_feedback import create_feedback, analyze_sentiment, categorize_feedback

def test_create():
    f = create_feedback(app_id="a1", user_id="u1", type="bug", message="Button doesn't work on mobile")
    assert f["status"] == "new"

def test_invalid_type():
    f = create_feedback(app_id="a1", user_id="u1", type="complaint", message="Something wrong")
    assert f["error"]

def test_positive():
    s = analyze_sentiment(message="This app is great and I love using it!")
    assert s["sentiment"] == "positive"

def test_negative():
    s = analyze_sentiment(message="This is terrible and broken")
    assert s["sentiment"] == "negative"

def test_categorize():
    fbs = [{"type": "bug", "sentiment": "negative"}, {"type": "praise", "sentiment": "positive"},
           {"type": "bug", "sentiment": "negative"}]
    r = categorize_feedback(feedbacks=fbs)
    assert r["by_type"]["bug"] == 2
    assert r["total"] == 3
