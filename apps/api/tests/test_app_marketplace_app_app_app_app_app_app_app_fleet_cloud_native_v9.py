from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_native_v9 import fleet_cloud_native_v9
def test_cn_v9():
    r = fleet_cloud_native_v9([{"containerized": True, "serverless": False, "maturity_score": 4.5}])
    assert r["containerized"] == 1
    assert r["avg_maturity"] == 4.5
    assert r["healthy"]
