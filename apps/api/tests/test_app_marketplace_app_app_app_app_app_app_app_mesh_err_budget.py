from app.services.app_marketplace_app_app_app_app_app_app_app_mesh_err_budget import check_mesh_err_budget
def test_check():
    r = check_mesh_err_budget([{"budget_consumed_pct": 50}, {"budget_consumed_pct": 110}])
    assert r["exhausted"] == 1
    assert not r["all_within"]
