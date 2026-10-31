from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_labelstudio import fleet_labelstudio_status
def test_ls():
    r = fleet_labelstudio_status([{"running": True, "projects": 30, "annotations": 500000}])
    assert r["projects"] == 30
    assert r["all_running"]
