from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_data_validation_v9 import fleet_api_data_validation_v9
def test_adv2_v9():
    r = fleet_api_data_validation_v9([{"active": True, "anomalies_detected": 0, "records_validated": 100000}])
    assert r["anomalies"] == 0
    assert r["healthy"]
