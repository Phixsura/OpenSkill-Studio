from app.services.app_marketplace_app_developer_welcome_wizard import build_welcome_flow

def test_beginner():
    f = build_welcome_flow(experience="beginner", goals=["publish_app"])
    assert f["step_count"] == 5
    assert f["experience"] == "beginner"

def test_expert():
    f = build_welcome_flow(experience="expert", goals=["api"])
    assert f["step_count"] == 3

def test_invalid_defaults_beginner():
    f = build_welcome_flow(experience="unknown", goals=[])
    assert f["experience"] == "beginner"
