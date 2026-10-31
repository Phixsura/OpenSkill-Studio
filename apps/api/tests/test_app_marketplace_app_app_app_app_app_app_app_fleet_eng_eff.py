from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eng_eff import fleet_eng_effectiveness
def test_eff():
    r = fleet_eng_effectiveness({"velocity_pct": 80, "quality_pct": 90, "delivery_pct": 70})
    assert r["score"] == 80.0
    assert r["effective"]
