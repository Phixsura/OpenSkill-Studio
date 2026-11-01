from app.services.app_marketplace_app_app_schema_migration import create_migration, build_migration_history

def test_create():
    r = create_migration(name="Add users table", up_sql="CREATE TABLE users...", down_sql="DROP TABLE users")
    assert "add_users_table" in r["id"]
    assert r["status"] == "pending"

def test_history():
    migrations = [
        {"id": "001", "status": "applied"},
        {"id": "002", "status": "applied"},
        {"id": "003", "status": "pending"},
    ]
    r = build_migration_history(migrations=migrations)
    assert r["applied"] == 2
    assert r["pending"] == 1
    assert r["needs_migration"]
    assert r["latest"] == "002"
