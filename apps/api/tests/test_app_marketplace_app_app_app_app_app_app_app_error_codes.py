from app.services.app_marketplace_app_app_app_app_app_app_app_error_codes import get_error, build_error_response, list_codes

def test_get():
    e = get_error("AUTH_001")
    assert e["message"] == "Invalid credentials"
    assert e["status"] == 401

def test_build():
    r = build_error_response("APP_001", detail="App ID: xyz")
    assert r["error"]["code"] == "APP_001"
    assert r["status"] == 404
    assert r["error"]["detail"] == "App ID: xyz"

def test_list():
    all_codes = list_codes()
    assert len(all_codes) == 11
    auth_codes = list_codes(category="auth")
    assert len(auth_codes) == 3
