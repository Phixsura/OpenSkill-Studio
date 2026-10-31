from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hedging import fleet_request_hedging
def test_hedge():
    r = fleet_request_hedging([{"hedged_requests": 1000, "saved_by_hedge": 200}])
    assert r["effectiveness_pct"] == 20.0
    assert r["worthwhile"]
