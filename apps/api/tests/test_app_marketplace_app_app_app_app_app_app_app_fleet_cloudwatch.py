from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloudwatch import fleet_cloudwatch_status
def test_cw():
    r = fleet_cloudwatch_status([{"state": "OK"}, {"state": "ALARM"}, {"state": "OK"}])
    assert r["alarm"] == 1
    assert not r["calm"]
