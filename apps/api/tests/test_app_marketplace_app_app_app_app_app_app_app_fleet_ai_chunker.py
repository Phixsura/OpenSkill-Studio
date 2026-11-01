from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_chunker import fleet_ai_chunker
def test_ch():
    r = fleet_ai_chunker([{"active": True, "docs_24h": 1000000, "chunks": 50000000, "avg_tokens": 512}])
    assert r["chunks"] == 50000000
    assert r["processing"]
