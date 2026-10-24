from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ab_result import fleet_ab_results
def test_ab():
    r = fleet_ab_results([{"result": "winner"}, {"result": "loser"}, {"result": "inconclusive"}, {"result": "winner"}])
    assert r["winners"] == 2
    assert r["win_rate"] == 50.0
