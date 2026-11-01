from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_aws_batch import fleet_aws_batch
def test_batch():
    r = fleet_aws_batch([{"state": "ENABLED", "submitted": 100, "running": 50, "succeeded": 500}])
    assert r["succeeded"] == 500
