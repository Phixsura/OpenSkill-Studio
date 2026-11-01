from app.services.app_marketplace_app_app_app_app_app_app_app_feedback_coll import (
    submit_feedback, analyze_feedback, clear_feedback,
)

def test_submit():
    clear_feedback()
    r = submit_feedback("u1", "ui", 5, "Great app!")
    assert r["submitted"]
    assert "<" not in r["comment"]
    r2 = submit_feedback("u2", "ui", 0, "bad")
    assert not r2["submitted"]
    clear_feedback()

def test_analyze():
    clear_feedback()
    submit_feedback("u1", "ui", 5, "love it")
    submit_feedback("u2", "ui", 4, "nice")
    submit_feedback("u3", "ui", 2, "meh")
    r = analyze_feedback("ui")
    assert r["count"] == 3
    assert r["avg_rating"] == 3.7
    assert r["nps"] == 33  # 2 promoters - 1 detractor / 3 * 100
    clear_feedback()
