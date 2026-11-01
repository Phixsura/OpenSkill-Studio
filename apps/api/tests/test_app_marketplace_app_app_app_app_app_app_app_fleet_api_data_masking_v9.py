from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_data_masking_v9 import fleet_api_data_masking_v9
def test_adm2_v9():
    r = fleet_api_data_masking_v9([{"masking_enabled": True, "pii_fields_masked": 10, "violations": 0}])
    assert r["masked"] == 1
    assert r["healthy"]
