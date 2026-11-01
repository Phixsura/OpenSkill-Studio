from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_chatbot_fw import fleet_ai_chatbot_framework
def test_cb():
    r = fleet_ai_chatbot_framework([{"active": True, "conversations_24h": 500000, "csat": 4.5, "containment_pct": 82}])
    assert r["csat"] == 4.5
    assert r["effective"]
