from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_docai import fleet_ai_docai
def test_docai():
    r = fleet_ai_docai([{"active": True, "pages_24h": 5000000, "fields_24h": 50000000}])
    assert r["pages_24h"] == 5000000
    assert r["all_active"]
