from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_aug import fleet_ai_data_augmentation
def test_da():
    r = fleet_ai_data_augmentation([{"active": True, "samples": 50000000, "multiplier": 10, "techniques": ["rotate", "flip", "crop", "color", "noise", "mix"]}])
    assert r["multiplier"] == 10.0
    assert r["diverse"]
