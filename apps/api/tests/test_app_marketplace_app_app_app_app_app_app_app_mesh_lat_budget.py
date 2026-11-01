from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_lat_budget import check_mesh_lat_budget
def test_check():
    r = check_mesh_lat_budget([{"actual_ms": 50, "budget_ms": 100}, {"actual_ms": 200, "budget_ms": 100}])
    assert r["over_budget"] == 1
    assert not r["all_within"]
