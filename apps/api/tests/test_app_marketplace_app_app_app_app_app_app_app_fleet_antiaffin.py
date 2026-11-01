from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_antiaffin import fleet_antiaffinity
def test_aa():
    r = fleet_antiaffinity([{"has_anti_affinity": True}, {"has_anti_affinity": False, "all_same_node": True}])
    assert r["with_anti_affinity"] == 1
    assert r["colocated_risk"] == 1
    assert not r["ha_compliant"]
