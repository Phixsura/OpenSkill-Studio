from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_hybrid_srch import fleet_ai_hybrid_search
def test_hs():
    r = fleet_ai_hybrid_search([{"active": True, "queries_24h": 10000000, "mrr": 0.92, "docs": 500000000}])
    assert r["mrr"] == 0.92
    assert r["accurate"]
