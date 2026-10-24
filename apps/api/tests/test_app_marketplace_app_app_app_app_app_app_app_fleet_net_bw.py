from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_net_bw import fleet_net_bandwidth
def test_bw():
    r = fleet_net_bandwidth([{"capacity_gbps": 10, "used_gbps": 8}, {"capacity_gbps": 10, "used_gbps": 9}])
    assert r["used_gbps"] == 17
    assert r["util_pct"] == 85.0
    assert r["saturated"]
