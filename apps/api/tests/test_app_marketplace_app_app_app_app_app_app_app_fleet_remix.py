from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_remix import fleet_remix_status
def test_rmx():
    r = fleet_remix_status([{"deployed": True, "loaders": 50, "actions": 30}])
    assert r["loaders"] == 50
    assert r["all_deployed"]
