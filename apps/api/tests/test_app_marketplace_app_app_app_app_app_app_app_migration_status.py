from app.services.app_marketplace_app_app_app_app_app_app_app_migration_status import (
    check_migration_status, estimate_migration_time,
)

def test_status():
    applied = [{"id": "001"}, {"id": "002"}]
    available = [{"id": "001"}, {"id": "002"}, {"id": "003", "destructive": True}]
    r = check_migration_status(applied, available)
    assert r["applied"] == 2
    assert r["pending"] == 1
    assert not r["up_to_date"]
    assert r["has_destructive"]
    assert r["latest_applied"] == "002"

def test_estimate():
    pending = [{"estimated_sec": 30, "requires_lock": False},
               {"estimated_sec": 120, "requires_lock": True}]
    r = estimate_migration_time(pending)
    assert r["estimated_sec"] == 150
    assert r["needs_downtime"]
    assert "2m" in r["estimated_display"]
