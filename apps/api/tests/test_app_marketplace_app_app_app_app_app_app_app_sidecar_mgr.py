from app.services.app_marketplace_app_app_app_app_app_app_app_sidecar_mgr import SidecarManager

def test_inject():
    sm = SidecarManager()
    r = sm.inject("api")
    assert r["status"] == "injected"
    assert r["mtls"]

def test_mtls():
    sm = SidecarManager()
    sm.inject("api")
    sm.configure_mtls("api", False)
    assert sm.stats()["mtls_enabled"] == 0

def test_policy():
    sm = SidecarManager()
    sm.inject("api")
    r = sm.traffic_policy("api", timeout_ms=3000, retries=5)
    assert r["policy"]["timeout_ms"] == 3000
