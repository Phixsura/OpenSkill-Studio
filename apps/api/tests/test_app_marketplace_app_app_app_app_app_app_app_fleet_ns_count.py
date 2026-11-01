from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ns_count import fleet_namespace_count
def test_ns():
    r = fleet_namespace_count([{"pod_count": 10}, {"pod_count": 0}, {"pod_count": 5}])
    assert r["active"] == 2
    assert r["empty"] == 1
    assert not r["needs_cleanup"]
