from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_priv import fleet_ai_data_privacy
def test_dp():
    r = fleet_ai_data_privacy([{"active": True, "epsilon": 0.5, "datasets": 100, "queries_24h": 1000000}])
    assert r["epsilon"] == 0.5
    assert r["private"]
