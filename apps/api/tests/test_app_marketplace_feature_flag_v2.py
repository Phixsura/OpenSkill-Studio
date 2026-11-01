from app.services.app_marketplace_feature_flag_v2 import evaluate_flag, get_all_flags, get_flag_status

def test_full_rollout():
    r = evaluate_flag(flag_id="new_search", user_id="u1")
    assert r["enabled"]

def test_disabled():
    r = evaluate_flag(flag_id="dark_mode_v2", user_id="u1")
    assert not r["enabled"]

def test_unknown():
    r = evaluate_flag(flag_id="nonexistent")
    assert not r["enabled"]

def test_deterministic():
    r1 = evaluate_flag(flag_id="ai_recommendations", user_id="user123")
    r2 = evaluate_flag(flag_id="ai_recommendations", user_id="user123")
    assert r1["enabled"] == r2["enabled"]

def test_all_flags():
    flags = get_all_flags(user_id="u1")
    assert "new_search" in flags
    assert flags["new_search"]

def test_status():
    s = get_flag_status()
    assert len(s) >= 5
