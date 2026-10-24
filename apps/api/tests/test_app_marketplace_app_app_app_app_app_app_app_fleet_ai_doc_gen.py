from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_doc_gen import fleet_ai_doc_gen
def test_dg():
    r = fleet_ai_doc_gen([{"active": True, "pages_24h": 10000, "repos": 500, "freshness_pct": 95}])
    assert r["pages_24h"] == 10000
    assert r["current"]
