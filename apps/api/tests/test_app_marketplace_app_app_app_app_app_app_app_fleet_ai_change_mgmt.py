from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_change_mgmt import fleet_ai_change_mgmt
def test_cm():
    r = fleet_ai_change_mgmt([{"active": True, "changes_24h": 50, "approved": 48, "rejected": 2}])
    assert r["approved"] == 48
    assert r["governed"]
