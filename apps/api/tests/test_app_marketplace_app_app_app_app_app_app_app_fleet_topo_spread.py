from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_topo_spread import fleet_topology_spread
def test_spread():
    r = fleet_topology_spread([{"zones": 3}, {"zones": 1}, {"zones": 2}])
    assert r["well_spread"] == 1
    assert r["single_zone"] == 1
    assert not r["resilient"]
