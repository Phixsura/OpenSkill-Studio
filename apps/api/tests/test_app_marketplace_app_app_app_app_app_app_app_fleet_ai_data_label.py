from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_label import fleet_ai_data_labeling
def test_dl():
    r = fleet_ai_data_labeling([{"active": True, "labeled_24h": 100000, "pending": 5000, "accuracy": 97.5}])
    assert r["labeled_24h"] == 100000
    assert r["quality"]
