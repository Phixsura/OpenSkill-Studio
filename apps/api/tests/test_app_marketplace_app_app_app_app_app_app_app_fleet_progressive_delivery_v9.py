from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_progressive_delivery_v9 import fleet_progressive_delivery_v9
def test_pd_v9():
    r = fleet_progressive_delivery_v9([{"phase": "completed"}, {"phase": "canary"}])
    assert r["completed"] == 1
    assert r["in_progress"] == 1
    assert r["healthy"]
