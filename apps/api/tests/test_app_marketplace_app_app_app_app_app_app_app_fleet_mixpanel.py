from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mixpanel import fleet_mixpanel_status
def test_mp():
    r = fleet_mixpanel_status([{"active": True, "events_24h": 5000000, "users": 100000}])
    assert r["events_24h"] == 5000000
    assert r["data_flowing"]
