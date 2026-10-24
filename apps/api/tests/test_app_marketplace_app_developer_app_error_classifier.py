from app.services.app_marketplace_app_developer_app_error_classifier import classify_error, aggregate_errors_by_category

def test_connection():
    r = classify_error(message="ECONNREFUSED: could not connect to host")
    assert r["category"] == "connection"
    assert r["severity"] == "high"

def test_auth():
    r = classify_error(message="401 Unauthorized: token expired")
    assert r["category"] == "auth"

def test_server():
    r = classify_error(message="500 Internal Server Error")
    assert r["category"] == "server"
    assert r["severity"] == "critical"

def test_unknown():
    r = classify_error(message="Something weird happened")
    assert r["category"] == "unknown"

def test_aggregate():
    errors = [{"message": "ECONNREFUSED"}, {"message": "ECONNREFUSED"}, {"message": "401 Unauthorized"}]
    r = aggregate_errors_by_category(errors=errors)
    assert r["top_category"] == "connection"
    assert r["categories"]["connection"] == 2
