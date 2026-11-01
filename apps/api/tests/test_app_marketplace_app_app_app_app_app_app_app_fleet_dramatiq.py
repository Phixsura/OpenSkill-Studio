from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dramatiq import fleet_dramatiq_status
def test_dr():
    r = fleet_dramatiq_status([{"online": True, "messages_24h": 100000, "workers": 20}])
    assert r["messages_24h"] == 100000
    assert r["all_online"]
