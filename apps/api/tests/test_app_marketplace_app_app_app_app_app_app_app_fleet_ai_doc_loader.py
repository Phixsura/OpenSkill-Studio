from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_doc_loader import fleet_ai_document_loader
def test_dl():
    r = fleet_ai_document_loader([{"active": True, "formats": ["pdf", "docx", "html", "md", "txt", "csv"], "docs_24h": 500000, "size_gb": 100}])
    assert r["formats"] == 6
    assert r["versatile"]
