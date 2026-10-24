from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_s3 import fleet_s3_status
def test_s3():
    r = fleet_s3_status([{"objects": 1000000, "size_tb": 5, "versioning": True, "encrypted": True}, {"objects": 500000, "size_tb": 2, "encrypted": False}])
    assert r["objects"] == 1500000
    assert not r["secure"]
