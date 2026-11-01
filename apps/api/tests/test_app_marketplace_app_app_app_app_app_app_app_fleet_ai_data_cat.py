from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_cat import fleet_ai_data_catalog
def test_dc():
    r = fleet_ai_data_catalog([{"active": True, "datasets": 5000, "tags": 10000, "searches_24h": 50000}])
    assert r["datasets"] == 5000
    assert r["discoverable"]
