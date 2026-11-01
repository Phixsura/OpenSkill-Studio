from app.services.app_marketplace_app_app_app_app_app_app_app_db_migrate_track import MigrationTracker

def test_lifecycle():
    mt = MigrationTracker()
    mt.register("001", "Create users table")
    mt.register("002", "Add email column")
    mt.register("003", "Drop legacy table", reversible=False)
    assert len(mt.pending()) == 3
    mt.apply("001")
    mt.apply("002")
    assert mt.status()["applied"] == 2
    assert mt.status()["pending"] == 1

def test_rollback():
    mt = MigrationTracker()
    mt.register("001", "test", reversible=True)
    mt.register("002", "irreversible", reversible=False)
    mt.apply("001")
    mt.apply("002")
    r1 = mt.rollback("001")
    assert r1["rolled_back"]
    r2 = mt.rollback("002")
    assert not r2["rolled_back"]
    assert r2["reason"] == "irreversible"
