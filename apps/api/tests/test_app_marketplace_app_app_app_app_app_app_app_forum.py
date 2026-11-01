from app.services.app_marketplace_app_app_app_app_app_app_app_forum import create_topic, build_forum_page

def test_topic():
    t = create_topic(title="How to use webhooks?", body="I need help with webhooks",
                       author="alice", category="help", tags=["webhooks"])
    assert t["title"] == "How to use webhooks?"
    assert t["category"] == "help"
    assert t["replies"] == 0

def test_forum():
    topics = [
        {"title": "Help", "category": "help", "views": 100, "likes": 5, "replies": 3},
        {"title": "Bug", "category": "bugs", "views": 50, "likes": 2, "replies": 0},
    ]
    r = build_forum_page(topics)
    assert r["total"] == 2
    unanswered = build_forum_page(topics, sort="unanswered")
    assert unanswered["total"] == 1
