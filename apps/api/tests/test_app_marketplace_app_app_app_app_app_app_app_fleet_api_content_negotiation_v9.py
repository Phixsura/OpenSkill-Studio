from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_content_negotiation_v9 import fleet_api_content_negotiation_v9
def test_acn_v9():
    r = fleet_api_content_negotiation_v9([{"content_type": "json", "multi_format": False, "xml_support": False}])
    assert r["json_only"] == 1
    assert r["healthy"]
