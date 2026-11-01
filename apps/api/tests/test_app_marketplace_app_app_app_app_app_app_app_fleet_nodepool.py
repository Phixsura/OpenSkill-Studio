from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nodepool import fleet_nodepool_utilization
def test_nodepool():
    r = fleet_nodepool_utilization([{"nodes": 10, "max_nodes": 10}, {"nodes": 5, "max_nodes": 20}])
    assert r["total_nodes"] == 15
    assert r["at_max"] == 1
    assert r["util_pct"] == 50.0
