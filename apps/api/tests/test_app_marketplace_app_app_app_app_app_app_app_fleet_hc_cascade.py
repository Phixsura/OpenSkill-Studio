from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hc_cascade import fleet_hc_cascade
def test_cascade():
    r = fleet_hc_cascade([{"healthy": False}, {"healthy": True, "impacted_by_dependency": True, "cascade_depth": 2},
                          {"healthy": True, "impacted_by_dependency": True, "cascade_depth": 3}])
    assert r["unhealthy"] == 1
    assert r["impacted"] == 2
    assert r["max_cascade_depth"] == 3
    assert r["cascading"]
