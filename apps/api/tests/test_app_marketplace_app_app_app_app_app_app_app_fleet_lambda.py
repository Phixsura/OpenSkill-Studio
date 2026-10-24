from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_lambda import fleet_lambda_status
def test_lambda():
    r = fleet_lambda_status([{"state": "Active", "invocations_24h": 5000000, "errors_24h": 0, "cold_start_pct": 2}])
    assert r["invocations_24h"] == 5000000
    assert r["healthy"]
