from app.services.app_marketplace_app_api_error_handler import create_error_response, classify_exception

def test_not_found():
    r = create_error_response(code="NOT_FOUND", detail="App xyz not found")
    assert r["error"]["status"] == 404
    assert r["error"]["code"] == "NOT_FOUND"
    assert "xyz" in r["error"]["message"]

def test_validation_with_field():
    r = create_error_response(code="VALIDATION_ERROR", detail="Too short", field="name")
    assert r["error"]["field"] == "name"
    assert r["error"]["status"] == 422

def test_classify_not_found():
    r = classify_exception(exc_type="NotFoundError", message="User not found")
    assert r["code"] == "NOT_FOUND"

def test_classify_conflict():
    r = classify_exception(exc_type="DBError", message="Duplicate key conflict")
    assert r["code"] == "CONFLICT"

def test_classify_unknown():
    r = classify_exception(exc_type="Error", message="Something broke")
    assert r["code"] == "INTERNAL_ERROR"
