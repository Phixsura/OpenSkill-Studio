from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_header_v9 import fleet_api_header_v9
def test_ah2_v9():
    r = fleet_api_header_v9([{"type": "security"}, {"type": "cors"}])
    assert r["security"] == 1
    assert r["healthy"]
