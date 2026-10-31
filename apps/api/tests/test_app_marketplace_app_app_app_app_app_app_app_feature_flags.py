from app.services.app_marketplace_app_app_app_app_app_app_app_feature_flags import evaluate_flags, is_flag_on

def test_evaluate():
    flags = [
        {"key": "dark_mode", "label": "Dark Mode", "enabled": True},
        {"key": "beta_ai", "label": "Beta AI", "enabled": True, "environments": ["staging"]},
        {"key": "old_ui", "label": "Old UI", "enabled": False},
    ]
    r = evaluate_flags(flags, env="production")
    assert r["enabled"] == 1
    assert r["disabled"] == 2
    assert r["flags"][0]["enabled"]  # dark_mode on in prod
    assert not r["flags"][1]["enabled"]  # beta_ai only staging

def test_is_flag_on():
    flags = [{"key": "x", "enabled": True}, {"key": "y", "enabled": False}]
    assert is_flag_on(flags, "x")
    assert not is_flag_on(flags, "y")
    assert not is_flag_on(flags, "missing")
