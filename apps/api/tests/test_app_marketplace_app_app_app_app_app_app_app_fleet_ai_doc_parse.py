from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_doc_parse import fleet_ai_doc_parsing
def test_dp():
    r = fleet_ai_doc_parsing([{"active": True, "docs_24h": 1000000, "fields": 50000000, "accuracy": 98}])
    assert r["fields"] == 50000000
    assert r["reliable"]
