from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gcp_dm import fleet_gcp_dm
def test_dm():
    r = fleet_gcp_dm([{"status": "DONE"}, {"status": "DONE"}, {"status": "FAILED"}])
    assert r["done"] == 2
    assert not r["healthy"]
