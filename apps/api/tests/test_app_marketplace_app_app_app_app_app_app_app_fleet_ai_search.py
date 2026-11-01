from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_search import fleet_ai_search
def test_ais():
    r = fleet_ai_search([{"active": True, "queries_24h": 5000000, "relevance_score": 92}])
    assert r["queries_24h"] == 5000000
    assert r["high_quality"]
