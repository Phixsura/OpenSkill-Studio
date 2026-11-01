from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_env_mgr import (
    list_environments, deploy_to_env, env_comparison,
)

def test_list():
    r = list_environments()
    assert r["total"] == 3

def test_deploy():
    r = deploy_to_env("staging", "2.0")
    assert r["deployed"]
    r2 = deploy_to_env("production", "2.0")
    assert not r2["deployed"]  # needs approval
    r3 = deploy_to_env("production", "2.0", "alice")
    assert r3["deployed"]

def test_comparison():
    r = env_comparison({"dev": {"version": "2.1"}, "staging": {"version": "2.0"}, "prod": {"version": "2.0"}})
    assert not r["in_sync"]
