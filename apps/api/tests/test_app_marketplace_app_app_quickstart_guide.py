from app.services.app_marketplace_app_app_quickstart_guide import build_quickstart

def test_fresh():
    r = build_quickstart()
    assert r["completed"] == 0
    assert r["progress_pct"] == 0
    assert r["next_step"]["id"] == "install"
    assert not r["all_done"]

def test_partial():
    r = build_quickstart(completed_steps=["install", "login"])
    assert r["completed"] == 2
    assert r["progress_pct"] == 40
    assert r["next_step"]["id"] == "init"

def test_all_done():
    r = build_quickstart(completed_steps=["install", "login", "init", "develop", "deploy"])
    assert r["all_done"]
    assert r["progress_pct"] == 100
