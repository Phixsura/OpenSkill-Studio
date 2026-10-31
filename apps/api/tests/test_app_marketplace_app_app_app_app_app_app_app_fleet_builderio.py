from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_builderio import fleet_builderio_status
def test_bio():
    r = fleet_builderio_status([{"active": True, "pages": 500, "components": 100}])
    assert r["pages"] == 500
    assert r["all_active"]
