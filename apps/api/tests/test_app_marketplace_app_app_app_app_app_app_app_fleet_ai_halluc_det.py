from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_halluc_det import fleet_ai_hallucination_detector
def test_hd():
    r = fleet_ai_hallucination_detector([{"active": True, "checked_24h": 5000000, "hallucinations": 5000, "detection_rate": 95}])
    assert r["checked_24h"] == 5000000
    assert r["vigilant"]
