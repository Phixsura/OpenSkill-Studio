from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_opentofu import fleet_opentofu_status
def test_ot():
    r = fleet_opentofu_status([{"plan_changes": 0, "resources": 50}, {"plan_changes": 3, "resources": 30}])
    assert r["clean"] == 1
    assert r["total_resources"] == 80
    assert not r["all_clean"]
