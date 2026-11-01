from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_evhub_v2 import fleet_ai_event_hub_v2
def test_ehv2():
    r = fleet_ai_event_hub_v2([{"active": True, "events_24h": 5000000000, "topics": 500, "consumers": 2000}])
    assert r["events_24h"] == 5000000000
    assert r["streaming"]
