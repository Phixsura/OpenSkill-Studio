from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_summarize import fleet_ai_summarization
def test_sum():
    r = fleet_ai_summarization([{"active": True, "docs_24h": 500000, "compression_ratio": 8.5, "rouge_l": 0.85}])
    assert r["rouge_l"] == 0.85
    assert r["quality"]
