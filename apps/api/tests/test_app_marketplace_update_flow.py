from app.services.app_marketplace_update_flow import check_update_compatibility, migrate_config, execute_update

def test_compatible():
    r = check_update_compatibility(
        current_version={"features": ["a"], "config_schema_version": 1},
        target_version={"breaking_changes": [], "deprecated_features": [], "config_schema_version": 1})
    assert r["compatible"]
    assert not r["requires_config_migration"]

def test_breaking():
    r = check_update_compatibility(
        current_version={"features": [], "config_schema_version": 1},
        target_version={"breaking_changes": [{"desc": "removed X"}], "deprecated_features": [], "config_schema_version": 2})
    assert not r["compatible"]
    assert r["requires_config_migration"]

def test_migrate_rename():
    r = migrate_config(old_config={"old_key": "val"}, migration_rules=[{"type": "rename", "from": "old_key", "to": "new_key"}])
    assert r["config"]["new_key"] == "val"
    assert "old_key" not in r["config"]

def test_migrate_default():
    r = migrate_config(old_config={}, migration_rules=[{"type": "default", "key": "timeout", "value": 30}])
    assert r["config"]["timeout"] == 30

def test_migrate_remove():
    r = migrate_config(old_config={"legacy": True, "keep": 1}, migration_rules=[{"type": "remove", "key": "legacy"}])
    assert "legacy" not in r["config"]
    assert r["config"]["keep"] == 1

def test_execute():
    r = execute_update(installation_id="inst_1", target_version_id="v2", new_config={"k": "v"})
    assert r["status"] == "active"
    assert r["rollback_available"]
