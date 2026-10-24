from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rel_score import fleet_ai_reliability_score
def test_rs():
    r = fleet_ai_reliability_score([{"active": True, "score": 98, "availability": 99.99, "durability": 99.999}])
    assert r["score"] == 98.0
    assert r["excellent"]
