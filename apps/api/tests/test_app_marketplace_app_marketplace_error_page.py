from app.services.app_marketplace_app_marketplace_error_page import build_error_page

def test_404():
    r = build_error_page(status_code=404)
    assert r["title"] == "Not Found"
    assert not r["show_support_link"]

def test_500():
    r = build_error_page(status_code=500)
    assert r["title"] == "Server Error"
    assert r["show_support_link"]

def test_custom_message():
    r = build_error_page(status_code=403, message="Custom: no access")
    assert r["message"] == "Custom: no access"
