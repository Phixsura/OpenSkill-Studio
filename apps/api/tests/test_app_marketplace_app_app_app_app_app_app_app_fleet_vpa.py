from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_vpa import fleet_vpa_status
def test_vpa():
    r = fleet_vpa_status([{"providing_recommendations": True, "mode": "Auto", "monthly_savings_usd": 500}])
    assert r["auto_mode"] == 1
    assert r["monthly_savings"] == 500
    assert r["effective"]
