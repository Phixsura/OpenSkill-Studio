from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_runbook import fleet_ai_runbook
def test_rb():
    r = fleet_ai_runbook([{"active": True, "executions_24h": 200, "auto_resolved": 180, "avg_duration_s": 45}])
    assert r["auto_resolved"] == 180
    assert r["automated"]
