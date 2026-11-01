from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_split_io import fleet_split_status
def test_split():
    r = fleet_split_status([{"active": True, "has_metrics": True, "treatments": 3}, {"active": True, "has_metrics": False, "treatments": 2}])
    assert r["with_metrics"] == 1
    assert r["treatments"] == 5
    assert not r["data_driven"]
