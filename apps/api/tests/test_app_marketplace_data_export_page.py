from app.services.app_marketplace_data_export_page import build_data_export_page, request_export

def test_page():
    p = build_data_export_page(user={"display_name": "Alice", "email": "alice@test.com"},
                                  available_exports=[], recent_exports=[])
    assert p["page_type"] == "data_export"
    assert len(p["available_exports"]) == 5
    assert p["gdpr_info"]["retention_days"] == 30

def test_export():
    r = request_export(user_id="u1", export_type="profile", format="json")
    assert r["success"]
    assert r["estimated_minutes"] == 5

def test_full_export():
    r = request_export(user_id="u1", export_type="full", format="zip")
    assert r["estimated_minutes"] == 30

def test_invalid():
    r = request_export(user_id="u1", export_type="secret", format="json")
    assert not r["success"]
