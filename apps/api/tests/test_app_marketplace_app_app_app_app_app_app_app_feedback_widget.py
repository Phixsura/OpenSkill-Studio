from app.services.app_marketplace_app_app_app_app_app_app_app_feedback_widget import collect_feedback, summarize_feedback

def test_collect():
    r = collect_feedback(page="/dashboard", reaction="love", comment="Great!")
    assert r["collected"]
    assert r["emoji"] == "😍"

def test_summarize():
    feedbacks = [
        {"reaction": "love"}, {"reaction": "love"}, {"reaction": "like"},
        {"reaction": "meh"}, {"reaction": "dislike"},
    ]
    r = summarize_feedback(feedbacks)
    assert r["total"] == 5
    assert r["satisfaction_pct"] == 60
    assert r["top_reaction"] == "love"
