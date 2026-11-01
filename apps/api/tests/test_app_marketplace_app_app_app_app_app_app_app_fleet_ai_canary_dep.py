from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_canary_dep import fleet_ai_canary_deploy
def test_cd():
    r = fleet_ai_canary_deploy([{"active": True, "canary_pct": 10, "rollbacks": 0, "promotions": 5}])
    assert r["canary_pct"] == 10.0
    assert r["safe"]
