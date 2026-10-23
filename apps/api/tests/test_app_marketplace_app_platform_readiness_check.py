from app.services.app_marketplace_app_platform_readiness_check import run_platform_readiness_check

def test_readiness():
    r = run_platform_readiness_check()
    assert "FULLY OPERATIONAL" in r["status"]
    assert r["subsystem_count"] == 8
    assert r["milestone"] == "1000 COMMITS ACHIEVED"
    assert all(s["status"] == "ready" for s in r["subsystems"].values())
