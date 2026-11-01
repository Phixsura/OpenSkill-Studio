from app.services.app_marketplace_developer_community import create_discussion, get_community_stats

def test_create():
    r = create_discussion(author_id="u1", title="How to use webhooks?", body="I need help with...", category="help")
    assert r["discussion_id"].startswith("disc_")
    assert r["category"] == "help"

def test_create_invalid():
    r = create_discussion(author_id="u1", title="Hi", body="x")
    assert "error" in r

def test_stats():
    discussions = [
        {"author_id": "u1", "category": "help", "solved": True},
        {"author_id": "u1", "category": "general", "solved": False},
        {"author_id": "u2", "category": "help", "solved": True},
    ]
    r = get_community_stats(discussions=discussions)
    assert r["total_discussions"] == 3
    assert r["solve_rate"] == 66.7
    assert r["top_contributors"][0]["user_id"] == "u1"
