from app.services.app_marketplace_app_app_app_app_app_app_app_migration_tracker import MigrationTracker

def test_migration_lifecycle():
    t = MigrationTracker()
    t.register(version="001", description="Create users", sql_up="CREATE TABLE users", sql_down="DROP TABLE users")
    t.register(version="002", description="Add email", sql_up="ALTER TABLE users ADD email", sql_down="ALTER TABLE users DROP email")
    s = t.status()
    assert s["pending"] == 2
    t.apply("001")
    assert t.status()["current_version"] == "001"
    t.apply("002")
    assert t.status()["current_version"] == "002"
    assert t.status()["applied"] == 2
    t.rollback("002")
    assert t.status()["current_version"] == "001"
    assert t.status()["pending"] == 1
