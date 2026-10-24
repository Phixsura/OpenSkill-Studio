from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_crewai import fleet_crewai_status
def test_cai():
    r = fleet_crewai_status([{"active": True, "agents": 10, "tasks_completed_24h": 5000}])
    assert r["agents"] == 10
    assert r["productive"]
