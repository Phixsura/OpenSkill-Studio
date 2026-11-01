from app.services.app_marketplace_onboarding_complete import build_onboarding_complete

def test_complete():
    p = build_onboarding_complete(
        developer={"display_name": "Alice"},
        first_app={"name": "MyApp", "status": "published"}, stats={})
    assert "Alice" in p["message"]
    assert len(p["achievements"]) == 4
    assert p["show_confetti"]
    assert len(p["next_steps"]) == 4

def test_no_app():
    p = build_onboarding_complete(developer={"display_name": "Bob"}, first_app=None, stats={})
    assert len(p["achievements"]) == 2
