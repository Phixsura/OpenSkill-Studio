from app.services.app_marketplace_app_app_app_app_app_app_app_app_app_feature_flags_page import build_feature_flags_page, evaluate_flag

def test_page():
    flags = [
        {"key": "dark_mode", "description": "Dark theme", "enabled": True, "rollout_pct": 100},
        {"key": "new_ui", "description": "New interface", "enabled": False, "rollout_pct": 50},
    ]
    r = build_feature_flags_page(flags=flags)
    assert r["total"] == 2
    assert r["enabled"] == 1

def test_evaluate():
    r = evaluate_flag(flag_key="test", user_id="u1", rollout_pct=100, enabled=True)
    assert r["enabled"]
    assert r["reason"] == "full_rollout"

def test_disabled():
    r = evaluate_flag(flag_key="x", user_id="u1", enabled=False)
    assert not r["enabled"]
