from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_fault import MeshFaultInjector

def test_inject():
    mfi = MeshFaultInjector()
    mfi.add_rule("api", "db", "latency", percentage=100, config={"delay_ms": 500})
    r = mfi.should_inject("api", "db", "req-1")
    assert r["inject"]
    assert r["fault_type"] == "latency"
    assert r["config"]["delay_ms"] == 500

def test_no_match():
    mfi = MeshFaultInjector()
    mfi.add_rule("api", "db", "error")
    r = mfi.should_inject("web", "api", "req-1")
    assert not r["inject"]

def test_disable():
    mfi = MeshFaultInjector()
    mfi.add_rule("a", "b", "error")
    mfi.add_rule("c", "d", "latency")
    r = mfi.disable_all()
    assert r["disabled"] == 2
    assert mfi.stats()["active"] == 0
