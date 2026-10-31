from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_chaos import fleet_ai_chaos
def test_chaos():
    r = fleet_ai_chaos([{"active": True, "runs_24h": 500, "failures_found": 12, "systems": 25}])
    assert r["failures_found"] == 12
    assert r["thorough"]
