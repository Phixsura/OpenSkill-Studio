from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pdb import fleet_pdb_status
def test_pdb():
    r = fleet_pdb_status([{"disruptions_allowed": 1}, {"disruptions_allowed": 0}])
    assert r["violated"] == 1
    assert not r["all_compliant"]
