from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_oncall import fleet_ai_oncall
def test_oc():
    r = fleet_ai_oncall([{"active": True, "engineers": 20, "pages_24h": 15, "ack_min": 2}])
    assert r["engineers"] == 20
    assert r["responsive"]
