from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_siem_connector_v9 import fleet_siem_connector_v9
def test_siem_v9():
    r = fleet_siem_connector_v9([{"active": True, "events_forwarded": 500000, "dropped": 0}])
    assert r["events_forwarded"] == 500000
    assert r["healthy"]
