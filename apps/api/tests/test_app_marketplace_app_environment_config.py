from app.services.app_marketplace_app_environment_config import create_env_config, merge_configs, get_effective_config, diff_env_configs

def test_create():
    r = create_env_config(app_id="a1", environment="production", config={"debug": False})
    assert r["environment"] == "production"

def test_invalid_env():
    r = create_env_config(app_id="a1", environment="test", config={})
    assert r["error"]

def test_merge():
    r = merge_configs(base={"a": 1, "b": {"x": 1, "y": 2}}, override={"b": {"y": 99}, "c": 3})
    assert r["a"] == 1
    assert r["b"]["y"] == 99
    assert r["b"]["x"] == 1
    assert r["c"] == 3

def test_effective():
    r = get_effective_config(base_config={"debug": True, "timeout": 30},
                              env_overrides={"production": {"debug": False}}, environment="production")
    assert r["debug"] is False
    assert r["timeout"] == 30

def test_diff():
    d = diff_env_configs(env_a={"debug": True, "url": "http://dev"}, env_b={"debug": False, "url": "http://prod"})
    assert d["count"] == 2
