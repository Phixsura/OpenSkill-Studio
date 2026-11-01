from app.services.app_marketplace_app_developer_reward import evaluate_rewards

def test_some():
    stats = {"app_published_count": 3, "login_streak": 10, "revenue": 500}
    r = evaluate_rewards(stats=stats)
    assert r["earned_count"] == 2  # first_publish + streak_7
    assert r["total_xp"] == 250

def test_all():
    stats = {"app_published_count": 15, "helpful_reviews": 60, "bugs_reported": 20,
             "login_streak": 10, "revenue": 2000}
    r = evaluate_rewards(stats=stats)
    assert r["earned_count"] == 6
    assert r["level"] >= 4

def test_none():
    r = evaluate_rewards(stats={})
    assert r["earned_count"] == 0
    assert r["total_xp"] == 0
