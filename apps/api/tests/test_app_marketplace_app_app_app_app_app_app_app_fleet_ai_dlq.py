from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dlq import fleet_ai_dlq
def test_dlq():
    r = fleet_ai_dlq([{"active": True, "messages": 50, "retried": 45, "discarded": 5}])
    assert r["retried"] == 45
    assert r["clean"]
