from app.services.app_marketplace_app_app_app_app_app_app_app_rollback_mgr import (
    create_snapshot, rollback, list_snapshots,
)

def test_rollback():
    s1 = create_snapshot("1.0", {"db": "pg14", "cache": "redis6"})
    s2 = create_snapshot("2.0", {"db": "pg15", "cache": "redis7", "queue": "rabbitmq"})
    r = rollback(s2, s1)
    assert r["from_version"] == "2.0"
    assert r["to_version"] == "1.0"
    assert r["change_count"] == 3  # db, cache changed, queue removed

def test_list():
    snaps = [create_snapshot("1.0", {}), create_snapshot("2.0", {})]
    r = list_snapshots(snaps)
    assert r["total"] == 2
    assert r["latest"] == "2.0"
