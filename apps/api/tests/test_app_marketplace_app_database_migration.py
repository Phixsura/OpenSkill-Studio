from app.services.app_marketplace_app_database_migration import create_migration, get_migration_status, validate_migration

def test_create():
    r = create_migration(name="Add users table",
        up_sql="CREATE TABLE users (id SERIAL PRIMARY KEY);",
        down_sql="DROP TABLE users;")
    assert "add_users_table" in r["migration_id"]
    assert r["status"] == "pending"

def test_status():
    migrations = [
        {"migration_id": "001", "status": "applied"},
        {"migration_id": "002", "status": "applied"},
        {"migration_id": "003", "status": "pending"},
    ]
    r = get_migration_status(migrations=migrations)
    assert r["applied"] == 2
    assert r["pending"] == 1
    assert not r["up_to_date"]

def test_validate_ok():
    r = validate_migration(up_sql="ALTER TABLE users ADD COLUMN email TEXT;", down_sql="ALTER TABLE users DROP COLUMN email;")
    assert r["valid"]

def test_validate_dangerous():
    r = validate_migration(up_sql="DROP DATABASE production;", down_sql="-- noop")
    assert not r["valid"]
    assert any("DROP DATABASE" in e for e in r["errors"])
