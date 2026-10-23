from app.services.app_marketplace_app_app_error_code_registry import register_error, build_error_catalog

def test_register():
    r = register_error(code=1001, name="invalid_token", message="Token is invalid", http_status=401)
    assert r["category"] == "AUTH"
    assert r["machine_code"] == "ERR_INVALID_TOKEN"

def test_catalog():
    errors = [
        {"code": 1001, "name": "invalid_token", "message": "Bad token", "http_status": 401},
        {"code": 2001, "name": "missing_field", "message": "Field required", "http_status": 400},
        {"code": 3001, "name": "not_found", "message": "Resource not found", "http_status": 404},
    ]
    r = build_error_catalog(errors=errors)
    assert r["total"] == 3
    assert "AUTH" in r["by_category"]
    assert "INPUT" in r["by_category"]
