from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_falco import fleet_falco_status
def test_falco():
    r = fleet_falco_status([{"falco_running": True, "alerts_24h": 50, "critical_alerts": 2}])
    assert r["alerts_24h"] == 50
    assert r["critical"] == 2
    assert not r["clean"]
