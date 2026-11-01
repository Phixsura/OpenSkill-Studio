from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_svc_disc import fleet_ai_service_discovery
def test_sd():
    r = fleet_ai_service_discovery([{"active": True, "services": 500, "instances": 5000, "lookups_24h": 100000000}])
    assert r["services"] == 500
    assert r["discoverable"]
