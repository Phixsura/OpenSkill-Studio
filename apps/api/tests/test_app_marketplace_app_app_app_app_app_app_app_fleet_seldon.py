from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_seldon import fleet_seldon_status
def test_sel():
    r = fleet_seldon_status([{"available": True, "predictors": 5, "requests_24h": 500000}])
    assert r["predictors"] == 5
    assert r["all_available"]
