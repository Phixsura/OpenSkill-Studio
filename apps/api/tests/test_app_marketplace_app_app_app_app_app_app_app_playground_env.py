from app.services.app_marketplace_app_app_app_app_app_app_app_playground_env import (
    create_env, stop_env, list_envs, env_stats, clear_envs,
)

def test_lifecycle():
    clear_envs()
    e = create_env("alice", "nextjs")
    assert e["status"] == "running"
    assert e["template"] == "nextjs"
    r = stop_env(e["id"], "bob")
    assert not r["stopped"]  # not owner
    r2 = stop_env(e["id"], "alice")
    assert r2["stopped"]
    clear_envs()

def test_list_stats():
    clear_envs()
    create_env("alice")
    create_env("bob")
    assert len(list_envs("alice")) == 1
    assert len(list_envs()) == 2
    s = env_stats()
    assert s["running"] == 2
    clear_envs()
