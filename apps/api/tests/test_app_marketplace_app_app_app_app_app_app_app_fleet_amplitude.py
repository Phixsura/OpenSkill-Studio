from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_amplitude import fleet_amplitude_status
def test_amp():
    r = fleet_amplitude_status([{"active": True, "events_24h": 10000000, "charts": 200}])
    assert r["events_24h"] == 10000000
    assert r["all_active"]
