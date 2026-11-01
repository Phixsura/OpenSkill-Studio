from app.services.app_marketplace_app_app_app_app_app_app_app_outage_comms import create_update, build_status_page_data

def test_update():
    r = create_update("INC-1", "investigating", "Looking into it", ["api", "db"])
    assert r["created"]
    assert r["status"] == "investigating"

def test_status():
    incidents = [
        {"status": "investigating", "affected": ["api"]},
        {"status": "resolved", "affected": ["db"]},
    ]
    r = build_status_page_data(incidents)
    assert r["overall_status"] == "degraded"
    assert r["active_incidents"] == 1
    assert "api" in r["affected_services"]
