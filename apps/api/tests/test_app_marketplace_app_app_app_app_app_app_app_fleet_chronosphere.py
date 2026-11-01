from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chronosphere import fleet_chronosphere_status
def test_cs():
    r = fleet_chronosphere_status([{"active_series": 5000000, "savings_pct": 40}])
    assert r["active_series"] == 5000000
    assert r["cost_efficient"]
