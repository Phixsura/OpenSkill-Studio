from app.services.app_marketplace_app_app_app_app_app_app_app_command_bus import (
    register_handler, dispatch, command_stats, clear_bus,
)

def test_dispatch():
    clear_bus()
    register_handler("deploy.start", "deploy_handler")
    r = dispatch("deploy.start", {"version": "2.0"})
    assert r["dispatched"]
    assert r["handler"] == "deploy_handler"
    r2 = dispatch("unknown", {})
    assert not r2["dispatched"]
    clear_bus()

def test_stats():
    clear_bus()
    register_handler("a", "h1")
    dispatch("a", {})
    dispatch("a", {})
    s = command_stats()
    assert s["total_dispatched"] == 2
    assert s["by_command"]["a"] == 2
    clear_bus()
