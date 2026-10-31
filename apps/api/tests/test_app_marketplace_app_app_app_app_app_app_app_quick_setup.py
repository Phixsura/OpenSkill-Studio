from app.services.app_marketplace_app_app_app_app_app_app_app_quick_setup import generate_quick_setup

def test_setup():
    r = generate_quick_setup(app_name="My App", language="python")
    assert r["app_name"] == "My App"
    assert r["language"] == "python"
    assert "pip install" in r["install"]
    assert "OpenSkill" in r["code"]
    assert r["api_key"].startswith("sk_test_")
    assert len(r["next_steps"]) == 3
    assert r["estimated_time"] == "5 minutes"
