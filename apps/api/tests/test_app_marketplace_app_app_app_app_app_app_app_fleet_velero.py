from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_velero import fleet_velero_status
def test_velero():
    r = fleet_velero_status([{"phase": "Completed", "age_hours": 6}, {"phase": "Failed", "age_hours": 12}])
    assert r["completed"] == 1
    assert r["fresh"]
