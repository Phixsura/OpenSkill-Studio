from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_oncall_v7 import fleet_ai_oncall_v7
def test_ov7():
    r = fleet_ai_oncall_v7([{"active": True, "engineers": 50, "pages": 20, "ack_min": 1, "auto": 15}])
    assert r["engineers"] == 50
    assert r["responsive"]
