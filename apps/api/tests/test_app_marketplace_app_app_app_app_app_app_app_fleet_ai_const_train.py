from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_const_train import fleet_ai_constitutional
def test_ct():
    r = fleet_ai_constitutional([{"active": True, "principles": 50, "revisions_24h": 100000, "alignment": 96}])
    assert r["principles"] == 50
    assert r["aligned"]
