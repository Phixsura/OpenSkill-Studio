from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_storage_class import fleet_storage_class
def test_storage():
    r = fleet_storage_class([{"used_gb": 400, "allocated_gb": 500}, {"used_gb": 300, "allocated_gb": 500}])
    assert r["used_gb"] == 700
    assert r["pct"] == 70.0
    assert not r["pressure"]
