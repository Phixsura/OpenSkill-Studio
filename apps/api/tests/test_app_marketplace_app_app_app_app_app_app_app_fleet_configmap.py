from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_configmap import fleet_configmap_usage
def test_configmap():
    r = fleet_configmap_usage([{"size_bytes": 1024, "age_days": 10}, {"size_bytes": 2000000, "age_days": 100}])
    assert r["oversized"] == 1
    assert r["stale"] == 1
    assert not r["clean"]
