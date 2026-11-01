from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_input_enr import fleet_ai_input_enricher
def test_ie():
    r = fleet_ai_input_enricher([{"active": True, "enriched_24h": 5000000, "sources": 20, "added_tokens": 500}])
    assert r["enriched_24h"] == 5000000
    assert r["enriching"]
