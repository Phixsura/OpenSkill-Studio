from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_kg import fleet_ai_kg
def test_kg():
    r = fleet_ai_kg([{"active": True, "entities": 1000000, "relationships": 5000000, "queries_24h": 500000}])
    assert r["entities"] == 1000000
    assert r["relationships"] == 5000000
