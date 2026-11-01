from app.services.app_marketplace_app_app_error_page import build_error_page

def test_404():
    r = build_error_page(status_code=404)
    assert r["title"] == "Not Found"
    assert r["icon"] == "🔍"
    assert len(r["suggestions"]) == 3

def test_500():
    r = build_error_page(status_code=500, request_id="req_abc123")
    assert r["title"] == "Internal Server Error"
    assert r["request_id"] == "req_abc123"

def test_custom_message():
    r = build_error_page(status_code=403, custom_message="Org access required")
    assert r["description"] == "Org access required"

def test_unknown():
    r = build_error_page(status_code=418)
    assert r["title"] == "Error"
