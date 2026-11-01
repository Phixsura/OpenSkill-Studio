from app.services.app_marketplace_app_developer_rewards import award_points, compute_level, get_leaderboard

def test_award():
    r = award_points(developer_id="d1", action="first_app_published")
    assert r["points"] == 100
    assert r["badge"] == "🚀"

def test_unknown_action():
    r = award_points(developer_id="d1", action="magic")
    assert r["error"]

def test_level_beginner():
    l = compute_level(total_points=50)
    assert l["level"] == "Beginner"
    assert l["next_level"]["name"] == "Explorer"

def test_level_master():
    l = compute_level(total_points=1500)
    assert l["level"] == "Master"
    assert l["next_level"] is None

def test_leaderboard():
    devs = [{"name": "A", "points": 50}, {"name": "B", "points": 200}, {"name": "C", "points": 100}]
    lb = get_leaderboard(developers=devs)
    assert lb[0]["name"] == "B"
    assert lb[0]["rank"] == 1
