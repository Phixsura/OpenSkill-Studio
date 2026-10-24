from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_emb_idx import fleet_ai_emb_index
def test_ei():
    r = fleet_ai_emb_index([{"active": True, "vectors": 100000000, "searches_24h": 10000000, "avg_ms": 10}])
    assert r["vectors"] == 100000000
    assert r["fast"]
