from app.services.app_marketplace_app_app_app_app_app_app_app_api_migration import track_migration, migration_timeline

def test_track():
    r = track_migration("v1", "v2", [
        {"path": "/users", "migrated": True},
        {"path": "/orders", "migrated": True},
        {"path": "/legacy", "migrated": False},
    ])
    assert r["migrated"] == 2
    assert r["progress_pct"] == 67
    assert "/legacy" in r["deprecated_paths"]
    assert not r["complete"]

def test_timeline():
    r = migration_timeline([{"complete": True}, {"complete": False}])
    assert r["complete"] == 1
    assert r["in_progress"] == 1
