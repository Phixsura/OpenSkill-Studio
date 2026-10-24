from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_maturity_model_v9 import fleet_api_maturity_model_v9
def test_amm2_v9():
    r = fleet_api_maturity_model_v9([{"maturity_level": "L4"}, {"maturity_level": "L5"}])
    assert r["avg_level"] == 4.5
    assert r["healthy"]
