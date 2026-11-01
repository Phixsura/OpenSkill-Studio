from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_policy import MeshTrafficPolicy

def test_policy():
    mtp = MeshTrafficPolicy()
    mtp.set_policy("api", "db", timeout_ms=3000, retries=5)
    mtp.set_policy("api", "cache", timeout_ms=1000, retries=1)
    p = mtp.get_policy("api", "db")
    assert p["timeout_ms"] == 3000
    assert p["retries"] == 5
    assert mtp.stats()["total_policies"] == 2
    assert mtp.stats()["avg_timeout_ms"] == 2000

def test_default():
    mtp = MeshTrafficPolicy()
    p = mtp.get_policy("unknown", "unknown")
    assert p["timeout_ms"] == 5000
