from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_angular import fleet_angular_status
def test_ng():
    r = fleet_angular_status([{"deployed": True, "components": 200, "modules": 30, "bundle_kb": 500}])
    assert r["components"] == 200
    assert r["avg_bundle_kb"] == 500.0
