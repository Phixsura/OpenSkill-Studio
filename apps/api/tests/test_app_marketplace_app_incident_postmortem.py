from app.services.app_marketplace_app_incident_postmortem import create_postmortem, track_action_items

def test_create():
    p = create_postmortem(incident_id="inc_1", title="API Outage", summary="API was down for 30 min",
                           root_cause="Database connection pool exhausted",
                           timeline=[{"time": "10:00", "event": "Alerts fired"}],
                           action_items=[{"task": "Add connection pool monitoring", "status": "pending"}])
    assert p["status"] == "draft"
    assert p["root_cause"] == "Database connection pool exhausted"

def test_track():
    items = [{"task": "A", "status": "completed"}, {"task": "B", "status": "pending"}, {"task": "C", "status": "completed"}]
    r = track_action_items(items=items)
    assert r["completed"] == 2
    assert r["completion_pct"] == 67
