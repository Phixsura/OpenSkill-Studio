from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_text_cls import fleet_ai_text_classifier
def test_tc():
    r = fleet_ai_text_classifier([{"active": True, "classified_24h": 5000000, "labels": 100, "zero_shot_pct": 60, "f1": 0.92}])
    assert r["f1"] == 0.92
    assert r["accurate"]
