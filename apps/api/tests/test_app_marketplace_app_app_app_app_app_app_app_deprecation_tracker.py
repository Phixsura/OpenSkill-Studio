from app.services.app_marketplace_app_app_app_app_app_app_app_deprecation_tracker import DeprecationTracker

def test_tracker():
    t = DeprecationTracker()
    t.deprecate("/api/v1/users/search", sunset_date="2027-03-01",
                 replacement="/api/v2/users?q=", reason="New search API")
    t.track_usage("/api/v1/users/search", total_callers=100, migrated=75)
    s = t.summary()
    assert s["total_deprecated"] == 1
    assert s["items"][0]["migration_pct"] == 75
    assert s["items"][0]["remaining"] == 25
    assert not s["items"][0]["ready_to_sunset"]

def test_ready():
    t = DeprecationTracker()
    t.deprecate("/old", sunset_date="2027-01-01", replacement="/new")
    t.track_usage("/old", total_callers=50, migrated=50)
    assert t.summary()["ready_to_sunset"] == 1
