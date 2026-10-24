from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_degrade import fleet_graceful_degradation
def test_degrade():
    r = fleet_graceful_degradation([{"has_fallback": True, "fallback_active": True}, {"has_fallback": True}, {"has_fallback": False}])
    assert r["degraded"] == 1
    assert r["without_fallback"] == 1
    assert not r["all_protected"]
