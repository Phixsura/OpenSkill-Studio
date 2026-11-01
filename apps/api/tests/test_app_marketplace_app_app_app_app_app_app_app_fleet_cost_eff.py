from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_eff import fleet_cost_efficiency
def test_eff():
    r = fleet_cost_efficiency(100000, 8000)
    assert r["ratio"] == 12.5
    assert r["grade"] == "A"
    assert r["efficient"]
