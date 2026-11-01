from app.services.app_marketplace_app_app_app_app_app_app_app_multi_region import MultiRegionManager

def test_failover():
    mgr = MultiRegionManager()
    mgr.add_region("us-east", label="US East", is_primary=True)
    mgr.add_region("eu-west", label="EU West")
    assert mgr.status()["primary"] == "us-east"
    mgr.update_health("us-east", healthy=False)
    assert mgr.status()["primary"] == "eu-west"
    assert mgr.status()["status"] == "degraded"

def test_rebalance():
    mgr = MultiRegionManager()
    mgr.add_region("a", label="A", is_primary=True)
    mgr.add_region("b", label="B")
    s = mgr.status()
    assert s["regions"][0]["traffic_pct"] == 50
    assert s["regions"][1]["traffic_pct"] == 50
