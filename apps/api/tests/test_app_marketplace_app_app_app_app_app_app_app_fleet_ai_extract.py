from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_extract import fleet_ai_extraction
def test_ext():
    r = fleet_ai_extraction([{"active": True, "docs_24h": 500000, "entities_24h": 5000000}])
    assert r["docs_24h"] == 500000
    assert r["all_active"]
