from app.services.app_marketplace_app_app_data_retention import build_retention_policy, estimate_cleanup

def test_policy():
    types = [
        {"type": "logs", "description": "Application logs", "retention": "30d"},
        {"type": "events", "description": "User events", "retention": "1y"},
        {"type": "profiles", "description": "User profiles", "retention": "forever"},
    ]
    r = build_retention_policy(data_types=types)
    assert r["total"] == 3
    assert r["auto_delete_count"] == 2
    assert not r["policies"][2]["auto_delete"]

def test_cleanup():
    r = estimate_cleanup(record_count=50000, retention_days=30, daily_growth=100)
    assert r["eligible_for_deletion"] == 47000
    assert r["estimated_storage_saved_mb"] > 0
