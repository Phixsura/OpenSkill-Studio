from app.services.app_marketplace_app_migration_wizard import analyze_migration, build_migration_steps

def test_analyze():
    r = analyze_migration(
        source_app={"scopes": ["read", "write"], "event_types": ["install", "update"]},
        target_app={"scopes": ["read", "admin"], "event_types": ["install"]})
    assert r["scope_overlap"] == ["read"]
    assert r["missing_scopes"] == ["write"]
    assert r["compatibility_score"] == 50.0

def test_steps():
    analysis = {"new_scopes": ["admin"]}
    steps = build_migration_steps(analysis=analysis)
    actions = [s["action"] for s in steps]
    assert "install_target" in actions
    assert "grant_scopes" in actions
    assert actions[-1] == "uninstall_source"

def test_steps_no_config():
    steps = build_migration_steps(analysis={"new_scopes": []}, has_config=False)
    actions = [s["action"] for s in steps]
    assert "migrate_config" not in actions
