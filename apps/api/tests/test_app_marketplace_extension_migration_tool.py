from app.services.app_marketplace_extension_migration_tool import ExtMigrationToolService

def test_plan_and_execute():
    svc = ExtMigrationToolService()
    m = svc.plan("ext-1", "1.0", "2.0", [("Schema", "Update schema"), ("Data", "Migrate data")])
    assert len(m.steps) == 2
    svc.execute_step(m.migration_id, "s-1")
    svc.execute_step(m.migration_id, "s-2")
    p = svc.get_progress(m.migration_id)
    assert p["status"] == "completed"
    assert p["percentage"] == 100

def test_failure():
    svc = ExtMigrationToolService()
    m = svc.plan("ext-1", "1.0", "2.0", [("Step", "Do thing")])
    svc.execute_step(m.migration_id, "s-1", success=False, error="DB error")
    assert m.status == "failed"

def test_rollback():
    svc = ExtMigrationToolService()
    m = svc.plan("ext-1", "1.0", "2.0", [("A", "a"), ("B", "b")])
    svc.execute_step(m.migration_id, "s-1")
    svc.execute_step(m.migration_id, "s-2", success=False)
    assert svc.rollback(m.migration_id) is True
    assert m.status == "rolled_back"
