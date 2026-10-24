from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_statuspage_io import fleet_statuspage_io
def test_sp():
    r = fleet_statuspage_io([{"status": "operational", "active_incidents": 0}, {"status": "degraded", "active_incidents": 1}])
    assert r["operational"] == 1
    assert not r["all_green"]
