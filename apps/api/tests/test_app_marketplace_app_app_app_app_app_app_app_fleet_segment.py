from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_segment import fleet_segment_status
def test_seg():
    r = fleet_segment_status([{"active": True, "events_24h": 10000000, "sources": 20, "destinations": 15}])
    assert r["events_24h"] == 10000000
    assert r["sources"] == 20
