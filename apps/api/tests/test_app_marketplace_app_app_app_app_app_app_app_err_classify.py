from app.services.app_marketplace_app_app_app_app_app_app_app_err_classify import classify_error, error_distribution

def test_classify():
    assert classify_error("Connection timeout", 503)["class"] == "transient"
    assert classify_error("Invalid input", 400)["class"] == "client"
    assert classify_error("Internal server error", 500)["class"] == "server"
    assert classify_error("Resource not found", 404)["class"] == "data"

def test_distribution():
    errors = [
        {"message": "timeout", "status_code": 503},
        {"message": "invalid", "status_code": 400},
        {"message": "internal", "status_code": 500},
    ]
    r = error_distribution(errors)
    assert r["total"] == 3
    assert r["retryable"] == 2  # transient + server
