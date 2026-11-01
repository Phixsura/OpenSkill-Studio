from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rag import fleet_rag_status
def test_rag():
    r = fleet_rag_status([{"active": True, "queries_24h": 500000, "docs_indexed": 10000000}])
    assert r["queries_24h"] == 500000
    assert r["all_active"]
