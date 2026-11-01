from app.services.app_marketplace_app_app_app_app_app_app_app_env_switcher import get_environments, get_environment, compare_environments

def test_envs():
    envs = get_environments()
    assert len(envs) == 3

def test_get():
    e = get_environment("production")
    assert e["label"] == "Production"
    assert e["icon"] == "🚀"

def test_compare():
    r = compare_environments("staging", "production")
    assert r["promotion"]
    r2 = compare_environments("production", "staging")
    assert not r2["promotion"]
