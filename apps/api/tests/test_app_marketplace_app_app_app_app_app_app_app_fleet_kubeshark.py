from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kubeshark import fleet_kubeshark_status
def test_ks():
    r = fleet_kubeshark_status([{"active": True, "requests_captured": 50000, "anomalies_detected": 3}])
    assert r["requests_captured"] == 50000
    assert r["anomalies"] == 3
    assert not r["clean"]
