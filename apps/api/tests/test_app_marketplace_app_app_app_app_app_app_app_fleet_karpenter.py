from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_karpenter import fleet_karpenter_status
def test_kp():
    r = fleet_karpenter_status([{"active": True, "nodes_launched_24h": 10, "nodes_terminated_24h": 8, "savings_usd_24h": 500}])
    assert r["launched_24h"] == 10
    assert r["savings_24h"] == 500
