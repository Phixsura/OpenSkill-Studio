from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_litmus import fleet_litmus_status
def test_litmus():
    r = fleet_litmus_status([{"result": "Pass"}] * 8 + [{"result": "Fail"}] * 2)
    assert r["resilience_score"] == 80.0
    assert r["resilient"]
