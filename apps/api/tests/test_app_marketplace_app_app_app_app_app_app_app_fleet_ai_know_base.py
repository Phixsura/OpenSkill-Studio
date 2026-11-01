from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_know_base import fleet_ai_knowledge_base
def test_kb():
    r = fleet_ai_knowledge_base([{"active": True, "articles": 10000, "searches_24h": 500000, "helpful_pct": 92}])
    assert r["articles"] == 10000
    assert r["useful"]
