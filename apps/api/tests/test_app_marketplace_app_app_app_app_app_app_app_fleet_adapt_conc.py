from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_adapt_conc import fleet_adaptive_concurrency
def test_ac():
    r = fleet_adaptive_concurrency([{"current_limit": 100, "recently_adjusted": True}, {"current_limit": 200, "recently_adjusted": False}])
    assert r["avg_limit"] == 150.0
    assert r["recently_adjusted"] == 1
    assert not r["stable"]
