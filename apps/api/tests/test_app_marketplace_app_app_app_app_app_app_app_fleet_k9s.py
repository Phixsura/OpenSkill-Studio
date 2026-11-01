from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_k9s import fleet_k9s_usage
def test_k9s():
    r = fleet_k9s_usage([{"active_24h": True, "commands_24h": 500}, {"active_24h": True, "commands_24h": 300}])
    assert r["active_24h"] == 2
    assert r["commands_24h"] == 800
    assert not r["popular"]
