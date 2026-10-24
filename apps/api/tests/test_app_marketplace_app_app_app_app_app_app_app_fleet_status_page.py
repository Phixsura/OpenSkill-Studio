from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_status_page import fleet_status_page
def test_status():
    r = fleet_status_page([{"status": "operational"}, {"status": "operational"}, {"status": "degraded"}])
    assert r["operational"] == 2
    assert r["overall"] == "degraded"
