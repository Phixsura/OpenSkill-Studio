from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_summarizer import fleet_ai_summarizer
def test_sum():
    r = fleet_ai_summarizer([{"active": True, "docs_24h": 100000, "compression_ratio": 5}])
    assert r["docs_24h"] == 100000
    assert r["all_active"]
