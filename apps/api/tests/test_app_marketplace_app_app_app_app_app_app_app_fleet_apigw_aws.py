from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_apigw_aws import fleet_apigw_aws_status
def test_agw():
    r = fleet_apigw_aws_status([{"deployed": True, "requests_24h": 10000000, "throttled_24h": 50}])
    assert r["requests_24h"] == 10000000
    assert r["healthy"]
