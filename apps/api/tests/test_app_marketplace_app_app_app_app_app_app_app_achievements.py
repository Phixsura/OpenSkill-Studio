from app.services.app_marketplace_app_app_app_app_app_app_app_achievements import check_achievements, compute_level

def test_achievements():
    earned = check_achievements({"apps": 3, "deploys": 5, "users": 150, "api_calls": 2000000, "avg_response_ms": 80})
    assert len(earned) >= 4
    titles = [a["title"] for a in earned]
    assert "App Creator" in titles
    assert "Speed Demon" in titles
    assert "Million Calls" in titles

def test_level():
    assert compute_level(0)["title"] == "Newcomer"
    assert compute_level(25)["title"] == "Explorer"
    assert compute_level(75)["title"] == "Builder"
    assert compute_level(150)["title"] == "Expert"
    assert compute_level(250)["title"] == "Platform Master"
