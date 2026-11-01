from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_qa import fleet_ai_qa
def test_qa():
    r = fleet_ai_qa([{"active": True, "questions_24h": 5000000, "accuracy": 93, "sources": 10000000}])
    assert r["questions_24h"] == 5000000
    assert r["knowledgeable"]
