from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_output_encoding_v9 import fleet_api_output_encoding_v9
def test_aoe_v9():
    r = fleet_api_output_encoding_v9([{"output_encoded": True, "xss_safe": True, "responses_today": 100000}])
    assert r["encoded"] == 1
    assert r["healthy"]
