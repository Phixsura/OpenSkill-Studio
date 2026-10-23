from app.services.app_marketplace_app_app_app_app_app_app_app_error_classifier import classify_error, summarize_errors

def test_classify():
    assert classify_error("Unauthorized access", 401)["category"] == "auth"
    assert classify_error("Internal server error", 500)["category"] == "server"
    assert classify_error("Resource not found", 404)["category"] == "not_found"
    assert classify_error("Something weird")["category"] == "unknown"

def test_summarize():
    errors = [
        {"message": "timeout", "status_code": 500},
        {"message": "invalid input", "status_code": 422},
        {"message": "not found", "status_code": 404},
    ]
    r = summarize_errors(errors)
    assert r["total"] == 3
    assert r["has_critical"]
    assert r["by_category"]["server"] == 1
