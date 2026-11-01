from app.services.app_marketplace_app_developer_community import create_discussion, get_trending_discussions, get_community_stats

def test_create():
    d = create_discussion(author_id="u1", app_id="a1", title="How to use webhooks?",
                           body="I need help setting up webhooks", category="help")
    assert d["category"] == "help"

def test_invalid_category():
    d = create_discussion(author_id="u1", app_id=None, title="X", body="Y", category="spam")
    assert d["error"]

def test_trending():
    discussions = [{"title": "A", "upvotes": 10, "replies": 5},
                   {"title": "B", "upvotes": 1, "replies": 0},
                   {"title": "C", "upvotes": 5, "replies": 20}]
    t = get_trending_discussions(discussions=discussions)
    assert t[0]["title"] == "C"  # 5*2 + 20*3 = 70

def test_stats():
    discussions = [{"replies": 5}, {"replies": 10}]
    s = get_community_stats(discussions=discussions, members=100)
    assert s["total_replies"] == 15
    assert s["avg_replies"] == 7.5
