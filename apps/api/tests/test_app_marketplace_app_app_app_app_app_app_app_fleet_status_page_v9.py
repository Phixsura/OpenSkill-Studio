from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_status_page_v9 import fleet_status_page_v9
def test_sp2_v9():
    r = fleet_status_page_v9([{"status": "operational"}, {"status": "operational"}])
    assert r["operational"] == 2
    assert r["outage"] == 0
    assert r["healthy"]
