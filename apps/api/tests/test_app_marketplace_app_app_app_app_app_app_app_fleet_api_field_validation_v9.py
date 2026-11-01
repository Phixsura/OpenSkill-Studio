from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_field_validation_v9 import fleet_api_field_validation_v9
def test_afv_v9():
    r = fleet_api_field_validation_v9([{"active": True, "rejections_today": 100, "fields_validated": 50000}])
    assert r["fields_validated"] == 50000
    assert r["healthy"]
