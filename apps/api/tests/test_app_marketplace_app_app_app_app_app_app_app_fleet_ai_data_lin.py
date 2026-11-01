from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_data_lin import fleet_ai_data_lineage
def test_dl():
    r = fleet_ai_data_lineage([{"active": True, "datasets": 500, "transforms": 5000, "max_depth": 15}])
    assert r["datasets"] == 500
    assert r["traceable"]
