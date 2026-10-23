from app.services.app_marketplace_privacy_center import build_privacy_center, request_data_deletion

def test_center():
    p = build_privacy_center(
        user={"display_name": "Alice", "email": "alice@test.com"},
        data_categories=[{"name": "Profile", "items": 5}],
        consent={"analytics": True}, export_available=True)
    assert p["page_type"] == "privacy_center"
    assert len(p["sections"]) == 4
    assert len(p["sections"][2]["rights"]) == 6

def test_deletion():
    r = request_data_deletion(user_id="u1", reason="No longer using")
    assert r["status"] == "pending"
    assert r["confirmation_required"]
