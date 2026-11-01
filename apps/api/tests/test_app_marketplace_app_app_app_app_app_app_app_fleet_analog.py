from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_analog import fleet_analog_status
def test_analog():
    r = fleet_analog_status([{"deployed": True, "pages": 50, "api_routes": 20}])
    assert r["pages"] == 50
    assert r["fullstack"]
