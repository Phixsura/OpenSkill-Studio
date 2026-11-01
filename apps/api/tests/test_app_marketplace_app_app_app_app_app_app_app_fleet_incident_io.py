from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_incident_io import fleet_incident_io
def test_iio():
    r = fleet_incident_io([{"status": "resolved", "time_to_detect_min": 5, "time_to_resolve_min": 30}, {"status": "active"}])
    assert r["active"] == 1
    assert r["avg_ttd_min"] == 5.0
    assert r["avg_ttr_min"] == 30.0
