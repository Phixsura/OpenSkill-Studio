from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_honeycomb import fleet_honeycomb_status
def test_hc():
    r = fleet_honeycomb_status([{"active": True, "events_per_sec": 5000, "queries_24h": 500}])
    assert r["events_per_sec"] == 5000
    assert r["well_used"]
