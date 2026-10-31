from app.services.app_marketplace_app_onboarding_tour import get_tour

def test_fresh():
    r = get_tour()
    assert r["completed_count"] == 0
    assert r["current_step"]["id"] == "welcome"
    assert not r["tour_complete"]

def test_partial():
    r = get_tour(user_completed_steps=["welcome", "search"])
    assert r["completed_count"] == 2
    assert r["current_step"]["id"] == "categories"

def test_complete():
    all_ids = ["welcome", "search", "categories", "install", "dashboard", "done"]
    r = get_tour(user_completed_steps=all_ids)
    assert r["tour_complete"]
    assert r["current_step"] is None
