from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_exp import fleet_ai_experiments
def test_exp():
    r = fleet_ai_experiments([{"active": True, "variants": 3, "traffic_pct": 50}])
    assert r["variants"] == 3
    assert r["running"]
