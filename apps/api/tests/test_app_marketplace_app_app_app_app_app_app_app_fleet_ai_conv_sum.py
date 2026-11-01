from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_conv_sum import fleet_ai_conversation_summarizer
def test_cs():
    r = fleet_ai_conversation_summarizer([{"active": True, "summarized_24h": 2000000, "compression": 5, "retention_pct": 95}])
    assert r["summarized_24h"] == 2000000
    assert r["accurate"]
