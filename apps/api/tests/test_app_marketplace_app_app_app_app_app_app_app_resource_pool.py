from app.services.app_marketplace_app_app_app_app_app_app_app_resource_pool import ResourcePool

def test_allocate_release():
    p = ResourcePool("gpu", 10)
    r = p.allocate("team-a", 4)
    assert r["success"]
    assert r["remaining"] == 6
    r2 = p.allocate("team-b", 8)
    assert not r2["success"]
    p.release("team-a", 2)
    s = p.status()
    assert s["used"] == 2
    assert s["available"] == 8
    assert s["utilization_pct"] == 20.0
