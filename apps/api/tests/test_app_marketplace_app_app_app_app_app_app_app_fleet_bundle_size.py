from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bundle_size import fleet_bundle_size
def test_bundle():
    r = fleet_bundle_size([{"size_kb": 150}, {"size_kb": 300}, {"size_kb": 100}])
    assert r["total_kb"] == 550
    assert r["large"] == 1
    assert not r["optimized"]
