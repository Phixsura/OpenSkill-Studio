from app.services.app_marketplace_app_app_app_app_app_app_app_api_deprec import ApiDeprecationTracker

def test_deprecate_track():
    adt = ApiDeprecationTracker()
    adt.deprecate("/api/v1/users", "2027-01-01", replacement="/api/v2/users")
    adt.track_usage("/api/v1/users", "svc-a", migrated=True)
    adt.track_usage("/api/v1/users", "svc-b", migrated=False)
    status = adt.migration_status()
    assert status[0]["migration_pct"] == 50.0
    assert not status[0]["ready_to_sunset"]

def test_stats():
    adt = ApiDeprecationTracker()
    adt.deprecate("/old", "2027-06-01")
    adt.track_usage("/old", "x", migrated=True)
    s = adt.stats()
    assert s["total_deprecated"] == 1
    assert s["ready_to_sunset"] == 1
