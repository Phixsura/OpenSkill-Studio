from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_ops_excellence_v9 import fleet_api_ops_excellence_v9
def test_aoe2_v9():
    r = fleet_api_ops_excellence_v9()
    assert r["grade"] == "A+"
    assert r["dimensions"]["governance"] == 100
