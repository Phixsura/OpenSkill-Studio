from app.services.app_marketplace_app_developer_achievements import check_achievements, get_achievement_progress

def test_unlocked():
    r = check_achievements(stats={"apps_published": 3, "total_installs": 150, "has_five_star": True})
    ids = [a["id"] for a in r]
    assert "first_app" in ids
    assert "popular_100" in ids
    assert "multi_app" in ids

def test_none():
    r = check_achievements(stats={})
    assert len(r) == 0

def test_progress():
    p = get_achievement_progress(stats={"apps_published": 1})
    earned = [a for a in p if a["earned"]]
    assert len(earned) == 1
    assert earned[0]["id"] == "first_app"
    assert len(p) == 8
