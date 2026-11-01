from app.services.app_marketplace_app_app_app_app_app_app_app_api_errors import categorize_errors

def test_categorize():
    errors = [
        {"status": 404, "endpoint": "/api/users/999", "error_type": "not_found"},
        {"status": 500, "endpoint": "/api/apps", "error_type": "internal"},
        {"status": 500, "endpoint": "/api/apps", "error_type": "internal"},
        {"status": 422, "endpoint": "/api/users", "error_type": "validation"},
    ]
    r = categorize_errors(errors)
    assert r["total"] == 4
    assert r["client_errors"] == 2
    assert r["server_errors"] == 2
    assert r["top_endpoint"] == "/api/apps"
    assert r["by_status"][500] == 2
