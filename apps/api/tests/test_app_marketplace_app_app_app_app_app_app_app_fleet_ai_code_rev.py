from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_code_rev import fleet_ai_code_review
def test_cr():
    r = fleet_ai_code_review([{"active": True, "prs_24h": 5000, "suggestions": 15000, "accepted": 12000}])
    assert r["prs_24h"] == 5000
    assert r["accept_rate"] == 80.0
