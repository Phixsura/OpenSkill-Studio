from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eks import fleet_eks_status
def test_eks():
    r = fleet_eks_status([{"status": "ACTIVE", "fargate_profiles": 2, "managed_nodegroups": 3}])
    assert r["fargate_profiles"] == 2
    assert r["all_active"]
