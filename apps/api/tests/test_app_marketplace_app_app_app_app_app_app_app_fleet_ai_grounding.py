from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_grounding import fleet_ai_grounding
def test_gr():
    r = fleet_ai_grounding([{"active": True, "responses_24h": 10000000, "grounded_pct": 96, "sources": 50000000}])
    assert r["grounded_pct"] == 96.0
    assert r["reliable"]
