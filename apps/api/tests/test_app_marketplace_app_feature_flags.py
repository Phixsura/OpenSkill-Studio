from app.services.app_marketplace_app_feature_flags import create_flag, evaluate_flag, list_flags_status

def test_create():
    f = create_flag(app_id="a1", key="dark_mode", description="Enable dark mode", rollout_pct=50)
    assert f["key"] == "dark_mode"

def test_invalid_key():
    f = create_flag(app_id="a1", key="has spaces", description="X")
    assert f["error"]

def test_100_pct():
    assert evaluate_flag(flag={"key": "x", "rollout_pct": 100}, installation_id="any")

def test_0_pct():
    assert not evaluate_flag(flag={"key": "x", "rollout_pct": 0, "default_value": False}, installation_id="any")

def test_deterministic():
    flag = {"key": "test", "rollout_pct": 50}
    r1 = evaluate_flag(flag=flag, installation_id="inst1")
    r2 = evaluate_flag(flag=flag, installation_id="inst1")
    assert r1 == r2

def test_list():
    flags = [{"key": "a", "description": "A", "rollout_pct": 100},
             {"key": "b", "description": "B", "rollout_pct": 0, "default_value": False}]
    r = list_flags_status(flags=flags, installation_id="inst1")
    assert r[0]["enabled"]
    assert not r[1]["enabled"]
