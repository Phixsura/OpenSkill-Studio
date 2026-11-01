from app.services.app_marketplace_app_app_app_app_app_app_app_maintenance_window import MaintenanceScheduler

def test_maintenance():
    s = MaintenanceScheduler()
    w = s.schedule(title="DB Upgrade", start="2026-11-01T02:00Z", end="2026-11-01T04:00Z",
                    affected_services=["database", "api"], severity="full")
    assert w["status"] == "scheduled"
    assert len(s.upcoming()) == 1
    s.start_maintenance(w["id"])
    assert len(s.active()) == 1
    assert len(s.upcoming()) == 0
    s.complete(w["id"], notes="Completed successfully")
    assert len(s.active()) == 0
