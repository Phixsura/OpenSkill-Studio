from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_contentful import fleet_contentful_status
def test_cf():
    r = fleet_contentful_status([{"active": True, "entries": 50000, "api_calls_24h": 5000000}])
    assert r["entries"] == 50000
    assert r["all_active"]
