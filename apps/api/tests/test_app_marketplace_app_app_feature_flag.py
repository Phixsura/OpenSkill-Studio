from app.services.app_marketplace_app_app_feature_flag import evaluate_flag, list_flags

def test_full_rollout():
    r = evaluate_flag(flag_key="dark_mode", user_id="u1", percentage=100)
    assert r["enabled"]
    assert r["reason"] == "full_rollout"

def test_disabled():
    r = evaluate_flag(flag_key="x", user_id="u1", enabled=False)
    assert not r["enabled"]

def test_deterministic():
    r1 = evaluate_flag(flag_key="f", user_id="u1", percentage=50)
    r2 = evaluate_flag(flag_key="f", user_id="u1", percentage=50)
    assert r1["enabled"] == r2["enabled"]

def test_list():
    flags = [{"key": "a", "enabled": True}, {"key": "b", "enabled": False}]
    r = list_flags(flags=flags)
    assert r["total"] == 2
    assert r["active"] == 1
