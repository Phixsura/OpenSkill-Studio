from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_cur import fleet_ai_dataset_curator
def test_dc():
    r = fleet_ai_dataset_curator([{"active": True, "datasets": 100, "samples": 100000000, "quality": 95}])
    assert r["datasets"] == 100
    assert r["curated"]
