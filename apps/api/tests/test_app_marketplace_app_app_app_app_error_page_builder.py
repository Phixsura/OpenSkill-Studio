from app.services.app_marketplace_app_app_app_app_error_page_builder import build_error_page

def test_404():
    r = build_error_page(template="not_found", app_name="SuperApp")
    assert r["code"] == 404
    assert r["title"] == "Page Not Found"
    assert r["app_name"] == "SuperApp"

def test_custom_message():
    r = build_error_page(template="server_error", custom_message="Database connection failed")
    assert r["message"] == "Database connection failed"

def test_unknown_template():
    r = build_error_page(template="nonexistent")
    assert r["code"] == 500  # falls back to server_error

def test_request_id():
    r = build_error_page(template="server_error", request_id="req_abc123")
    assert r["request_id"] == "req_abc123"
