from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_eff import fleet_cost_efficiency
def test_eff():
    r = fleet_cost_efficiency(100000, 10000)
    assert r["ratio"] == 10.0
    assert r["grade"] == "A"
    assert r["efficient"]
