from app.services.app_marketplace_app_migration_tool import plan_migration, run_migration_check

def test_plan():
    changes = [
        {"description": "Rename field X to Y", "automated": True, "risk": "low"},
        {"description": "Update auth flow", "automated": False, "risk": "medium"},
    ]
    r = plan_migration(from_version="2.0", to_version="3.0", breaking_changes=changes)
    assert r["total_steps"] == 2
    assert r["automated_steps"] == 1
    assert not r["can_auto_migrate"]
    assert r["estimated_time_min"] == 30

def test_check():
    r = run_migration_check(app_id="a1", target_version="3.0")
    assert r["warnings"] == 1
    assert not r["ready"]
