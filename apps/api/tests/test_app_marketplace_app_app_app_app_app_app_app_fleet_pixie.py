from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pixie import fleet_pixie_status
def test_pixie():
    r = fleet_pixie_status([{"connected": True, "monitored_pods": 500, "data_retained_gb": 50}])
    assert r["monitored_pods"] == 500
    assert r["all_connected"]
