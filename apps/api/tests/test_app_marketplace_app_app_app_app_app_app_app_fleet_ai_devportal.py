from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_devportal import fleet_ai_devportal
def test_dp():
    r = fleet_ai_devportal([{"active": True, "docs_pages": 500, "api_keys": 10000, "developers": 5000}])
    assert r["docs_pages"] == 500
    assert r["developers"] == 5000
