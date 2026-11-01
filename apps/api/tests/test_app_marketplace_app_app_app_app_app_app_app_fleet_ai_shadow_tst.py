from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_shadow_tst import fleet_ai_shadow_test
def test_st():
    r = fleet_ai_shadow_test([{"active": True, "mirrored_24h": 2000000, "divergence_pct": 2.3}])
    assert r["mirrored_24h"] == 2000000
    assert r["consistent"]
