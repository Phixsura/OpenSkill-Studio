from app.services.app_marketplace_app_app_app_app_app_app_app_dep_change_track import track_dep_changes

def test_changes():
    r = track_dep_changes(
        {"api": ["db", "cache", "old-svc"], "worker": ["queue"]},
        {"api": ["db", "cache", "new-svc"], "worker": ["queue", "s3"]})
    assert r["services_affected"] == 2
    assert r["total_added"] == 2  # new-svc + s3
    assert r["total_removed"] == 1  # old-svc
    assert r["has_removals"]

def test_no_change():
    r = track_dep_changes({"api": ["db"]}, {"api": ["db"]})
    assert r["services_affected"] == 0
