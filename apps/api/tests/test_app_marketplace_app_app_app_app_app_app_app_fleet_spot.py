from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spot import fleet_spot_usage
def test_spot():
    r = fleet_spot_usage([{"type": "spot"}, {"type": "spot"}, {"type": "on-demand"}])
    assert r["spot"] == 2
    assert r["spot_pct"] == 66.7
    assert r["cost_optimized"]
