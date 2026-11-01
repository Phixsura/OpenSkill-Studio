from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_saga_orch import fleet_ai_saga_orchestrator
def test_so():
    r = fleet_ai_saga_orchestrator([{"active": True, "sagas_24h": 100000, "completed": 99000, "compensated": 1000}])
    assert r["completed"] == 99000
    assert r["reliable"]
