from app.services.app_marketplace_app_app_app_app_app_app_app_change_tracker import (
    record_change, get_recent_changes, clear_changes,
)

def test_record_get():
    clear_changes()
    record_change("api-service", "deployed", "alice", "v2.0 to production")
    record_change("config", "updated", "bob", "Changed timeout")
    record_change("api-service", "scaled", "alice", "3 → 5 replicas")
    r = get_recent_changes()
    assert r["total"] == 3
    r2 = get_recent_changes(entity="api-service")
    assert r2["total"] == 2
    clear_changes()
