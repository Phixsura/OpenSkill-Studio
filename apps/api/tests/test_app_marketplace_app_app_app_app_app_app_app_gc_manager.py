from app.services.app_marketplace_app_app_app_app_app_app_app_gc_manager import find_garbage, gc_stats

def test_find():
    r = find_garbage([
        {"id": "tmp-1", "age_hours": 100, "size_mb": 50, "type": "temp"},
        {"id": "active-1", "age_hours": 10, "size_mb": 200},
        {"id": "orphan-1", "age_hours": 5, "orphaned": True, "size_mb": 30, "type": "volume"},
    ])
    assert r["stale"] == 1
    assert r["orphaned"] == 1
    assert r["total_reclaimable_mb"] == 80

def test_stats():
    r = gc_stats([{"reclaimed_mb": 100, "items_cleaned": 5}, {"reclaimed_mb": 200, "items_cleaned": 10}])
    assert r["total_reclaimed_mb"] == 300
    assert r["total_items_cleaned"] == 15
