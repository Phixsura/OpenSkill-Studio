from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scaffolder import fleet_scaffolder_status
def test_sc():
    r = fleet_scaffolder_status([{"name": "service-template", "executions_30d": 40}, {"name": "lib-template", "executions_30d": 20}])
    assert r["executions_30d"] == 60
    assert r["top_template"] == "service-template"
    assert r["adopted"]
