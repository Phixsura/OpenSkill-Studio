from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_autogen import fleet_autogen_status
def test_ag():
    r = fleet_autogen_status([{"active": True, "conversations_24h": 10000, "agents": 20}])
    assert r["conversations_24h"] == 10000
    assert r["all_active"]
