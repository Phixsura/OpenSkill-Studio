from app.services.app_marketplace_app_app_app_app_app_app_app_migration_wizard import create_migration, run_step

def test_migration():
    m = create_migration(source="legacy-db", destination="new-db",
                          data_types=["users", "orders", "products"])
    assert m["total_steps"] == 3
    assert m["status"] == "ready"
    run_step(m, 0, records=1000)
    run_step(m, 1, records=5000, errors=3)
    r = run_step(m, 2, records=500)
    assert m["status"] == "completed"
    assert r["total_records"] == 6500
    assert r["total_errors"] == 3
    assert r["progress"] == "3/3"
