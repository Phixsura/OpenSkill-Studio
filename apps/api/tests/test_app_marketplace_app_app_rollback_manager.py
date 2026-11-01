from app.services.app_marketplace_app_app_rollback_manager import build_rollback_options, execute_rollback

def test_options():
    deps = [
        {"version": "2.0.0", "deployed_at": "2026-01-03", "commit": "abc123", "author": "Alice"},
        {"version": "1.5.0", "deployed_at": "2026-01-02", "commit": "def456", "author": "Bob"},
        {"version": "1.0.0", "deployed_at": "2026-01-01", "commit": "ghi789"},
    ]
    r = build_rollback_options(deployments=deps, current_version="2.0.0")
    assert r["can_rollback"]
    assert r["available"] == 2
    assert r["options"][0]["version"] == "1.5.0"

def test_no_options():
    r = build_rollback_options(deployments=[{"version": "1.0.0"}], current_version="1.0.0")
    assert not r["can_rollback"]

def test_execute():
    r = execute_rollback(target_version="1.5.0", reason="Bug in 2.0")
    assert r["status"] == "in_progress"
    assert r["target_version"] == "1.5.0"
