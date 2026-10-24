from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_backstage import fleet_backstage_adoption
def test_bs():
    r = fleet_backstage_adoption([{"in_backstage": True, "has_techdocs": True}, {"in_backstage": True}, {"in_backstage": False}])
    assert r["registered"] == 2
    assert r["with_techdocs"] == 1
    assert r["coverage_pct"] == 66.7
