from app.services.app_marketplace_app_app_app_app_app_app_app_region_failover import RegionFailoverCoordinator

def test_failover():
    rfc = RegionFailoverCoordinator()
    rfc.register_region("us-east", is_primary=True)
    rfc.register_region("eu-west")
    rfc.register_region("ap-south")
    r = rfc.failover("us-east")
    assert r["success"]
    assert r["new_primary"] == "eu-west"
    s = rfc.status()
    assert s["primary"] == "eu-west"
    assert "us-east" in s["failed"]

def test_failback():
    rfc = RegionFailoverCoordinator()
    rfc.register_region("us-east", is_primary=True)
    rfc.register_region("eu-west")
    rfc.failover("us-east")
    rfc.failback("us-east")
    assert rfc.status()["active"] == 2
