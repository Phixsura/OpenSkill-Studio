from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_governance_v9 import fleet_cloud_governance_v9
def test_cg2_v9():
    r = fleet_cloud_governance_v9([{"enforced": True, "violations": 5, "auto_remediated": 5}])
    assert r["violations"] == 5
    assert r["healthy"]
