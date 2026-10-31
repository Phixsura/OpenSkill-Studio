from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_appsync import fleet_appsync_status
def test_as():
    r = fleet_appsync_status([{"status": "ACTIVE", "requests_24h": 500000, "errors_4xx": 100, "errors_5xx": 0}])
    assert r["requests_24h"] == 500000
    assert r["healthy"]
